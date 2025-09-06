# API Key Setup Instructions

This project requires API keys to fetch sports data. Follow these steps to set up your API keys:

## 1. Create API Key File

1. Copy the example file:
   ```bash
   cp api_keys.txt.example api_keys.txt
   ```

2. Edit `api_keys.txt` and replace the placeholder values with your actual API keys.

## 2. Required API Keys

### SportsData.io NFL API Key
- **Purpose**: Fetches NFL game data, scores, and statistics
- **Get your key**: Visit [https://sportsdata.io/](https://sportsdata.io/) and sign up for an account
- **Configuration**: Set `NFL_API_KEY=your_actual_key` in `api_keys.txt`

## 3. File Security

- The `api_keys.txt` file is automatically ignored by git (listed in `.gitignore`)
- Never commit your actual API keys to the repository
- Keep your API keys secure and don't share them publicly

## 4. Testing Your Setup

After setting up your API keys, you can test the NFL data fetching by running:

```bash
cd src/Process-Data
python Get_Data.py
```

If configured correctly, you should see successful data fetching without 401 authentication errors.

## 5. Troubleshooting

- **401 Errors**: Check that your API key is correct and has sufficient quota
- **File Not Found**: Ensure `api_keys.txt` exists in the project root directory
- **Key Not Found**: Verify the key name matches exactly (case-sensitive)
