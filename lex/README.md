# Amazon Lex Bot Setup

This directory contains scripts and configurations for creating and testing the **PhotoSearchBot** Amazon Lex V2 bot.

## Bot Overview

- **Bot Name**: PhotoSearchBot
- **Purpose**: Natural language processing for photo search queries
- **Intent**: SearchIntent
- **Slot**: Keywords (captures search terms)

## Files

- `create-lex-bot.ps1` - Main script to create the Lex bot
- `test-lex-bot.ps1` - Test script to verify bot functionality
- `bot-config.json` - Bot configuration
- `intent-config.json` - Intent configuration with utterances
- `slot-type-config.json` - Custom slot type with synonyms

## Quick Start

### 1. Create the Bot

```powershell
.\lex\create-lex-bot.ps1
```

This will:
- Create the PhotoSearchBot
- Set up en_US locale
- Create SearchIntent with sample utterances
- Create Keywords slot
- Build the bot
- Create a production alias

### 2. Test the Bot

```powershell
.\lex\test-lex-bot.ps1
```

This tests the bot with various sample queries.

## Sample Utterances

The bot is trained to understand:

- `show me {Keywords}`
- `find photos of {Keywords}`
- `search for {Keywords}`
- `show me photos with {Keywords}`
- `{Keywords}` (direct keyword input)
- `find {Keywords}`
- `search {Keywords}`
- `photos of {Keywords}`

## Example Queries

Single keyword:
- "trees"
- "dogs"
- "beach"
- "sunset"

Multiple keywords:
- "dogs and kids"
- "cats and trees"
- "mountains and flowers"

Natural language:
- "show me dogs"
- "find photos of cats"
- "search for beach sunset"

## Integration with Lambda

The bot returns interpreted keywords that can be used by the search Lambda function:

```python
# In search-photos Lambda
lex_client = boto3.client('lexv2-runtime')

response = lex_client.recognize_text(
    botId='YOUR_BOT_ID',
    botAliasId='YOUR_ALIAS_ID',
    localeId='en_US',
    sessionId=session_id,
    text=user_query
)

keywords = response['sessionState']['intent']['slots']['Keywords']['value']['interpretedValue']
```

## Slot Type Strategy

The bot uses **AMAZON.AlphaNumeric** slot type which:
- Captures any alphanumeric input
- Allows flexibility for any search term
- No need to predefine all possible keywords
- Returns the original user input

Alternatively, you can use the custom **PhotoKeywords** slot type with predefined values and synonyms for better normalization.

## Bot Configuration Details

### Intent: SearchIntent
- **Confidence Threshold**: 0.4
- **Confirmation**: Not required
- **Fulfillment**: Returns slots immediately

### Slot: Keywords
- **Type**: AMAZON.AlphaNumeric (or custom PhotoKeywords)
- **Constraint**: Optional (allows single-word utterances)
- **Elicitation**: Minimal prompting

### Locale: en_US
- **NLU Confidence**: 0.4
- **Session Timeout**: 300 seconds

## Troubleshooting

### Bot Creation Fails
- Ensure you have proper IAM permissions for Lex V2
- Check if bot name already exists
- Verify the service-linked role exists

### Build Takes Too Long
- Bot building typically takes 1-2 minutes
- If it takes longer, check the AWS Console
- You can proceed with other tasks while it builds

### Testing Fails
- Make sure bot is fully built (status: Built or ReadyExpressTesting)
- Use the test alias (TSTALIASID) for testing
- Check bot ID is correct in bot-id.txt

## AWS Console Access

View and test your bot in the AWS Console:

```
https://console.aws.amazon.com/lexv2/home?region=us-east-1#bots
```

## Next Steps

1. **Test in Console**: Use the AWS Console test window to verify bot responses
2. **Update Lambda**: Add Lex integration to search-photos Lambda function
3. **Frontend Integration**: Update frontend to send queries through Lex
4. **Monitor**: Check CloudWatch logs for Lex interactions

## Cost Considerations

- **Lex V2 Pricing**: Pay per request
- **Free Tier**: 10,000 text requests per month for first year
- Typical usage for this project should stay within free tier

## Additional Resources

- [Lex V2 Documentation](https://docs.aws.amazon.com/lexv2/)
- [Lex V2 API Reference](https://docs.aws.amazon.com/lexv2/latest/APIReference/)
- [Building Bots](https://docs.aws.amazon.com/lexv2/latest/dg/building-bots.html)
