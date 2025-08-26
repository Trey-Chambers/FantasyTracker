# Fantasy Football Weekly Recap Generator

A robust Python script that automatically generates weekly recaps for ESPN fantasy football leagues and converts them to high-quality audio files using Google Text-to-Speech.

## Features

- 🏈 **Automatic Week Detection**: Intelligently determines the most recently completed week
- 📊 **Comprehensive Analysis**: Analyzes all matchups with detailed narratives
- 🏆 **Weekly Awards**: Generates awards for top performers, blowouts, and close games
- 🎵 **Audio Conversion**: Converts recaps to MP3 files using Google TTS
- 🛡️ **Robust Error Handling**: Gracefully handles API errors, network issues, and edge cases
- 🔒 **Secure Credential Management**: Uses environment variables for sensitive data

## Prerequisites

- Python 3.9 or higher
- ESPN Fantasy Football account
- Internet connection for API access

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd fantasy-football-recap-generator
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your credentials**
   
   Create a `.env` file in the same directory as the script with the following content:
   ```
   LEAGUE_ID=your_league_id_number
   ESPN_S2=your_espn_s2_cookie_value
   SWID=your_swid_cookie_value
   ```

## Getting Your Credentials

### League ID
1. Go to your ESPN Fantasy Football league
2. Look at the URL: `https://fantasy.espn.com/football/league?leagueId=123456789`
3. The number after `leagueId=` is your `LEAGUE_ID`

### ESPN S2 and SWID Cookies
1. Go to ESPN Fantasy Football and log in
2. Open browser developer tools (F12)
3. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Expand **Cookies** → **https://espn.com**
5. Find and copy the values for:
   - `ESPN_S2`
   - `SWID`

## Usage

### Basic Usage
```bash
python recap_generator.py
```

### What Happens
1. The script connects to ESPN's API using your credentials
2. Automatically determines the most recently completed week
3. Fetches all matchup data for that week
4. Generates a comprehensive narrative summary
5. Creates weekly awards (Manager of the Week, Blowout of the Week, etc.)
6. Converts the entire recap to an MP3 audio file
7. Saves the file as `recap_week_X.mp3`

### Sample Output
```
🎯 Fantasy Football Weekly Recap Generator
Loading credentials and connecting to ESPN...

============================================================
FANTASY FOOTBALL WEEKLY RECAP
============================================================
📊 WEEKLY RECAP FOR WEEK 4 📊

The Dragons triumphed over The Warriors with a final score of 145.67 to 132.45 (margin: 13.22 points).

The matchup between Thunder Cats and Gridiron Giants was a rare tie, with both teams scoring 128.90 points.

🏆 WEEKLY AWARDS 🏆
Manager of the Week: The Dragons with an incredible 145.67 points!
Blowout of the Week: The Dragons dominated The Warriors by 13.22 points (145.67 to 132.45)!
Nail-Biter of the Week: Thunder Cats vs Gridiron Giants was decided by just 0.50 points!
Sad Trombone Award: The Warriors with only 132.45 points. Better luck next week!
============================================================

✅ Successfully generated audio recap: recap_week_4.mp3
📁 File saved in: /path/to/your/directory
```

## Weekly Awards

The script automatically generates the following awards each week:

- **Manager of the Week**: Team with the highest score
- **Blowout of the Week**: Largest margin of victory
- **Nail-Biter of the Week**: Smallest margin of victory (excluding ties)
- **Sad Trombone Award**: Team with the lowest score

## Edge Cases Handled

- **Ties**: Properly recognized and narrated
- **Multiple Winners**: Awards shared when teams tie for honors
- **Pre-Season**: Graceful handling when no games have been played
- **API Errors**: Clear error messages for connection issues
- **Invalid Credentials**: Helpful guidance for authentication problems
- **Network Issues**: Robust error handling for connectivity problems

## Troubleshooting

### Common Issues

**"Failed to connect to ESPN API"**
- Check your internet connection
- Verify your credentials in the `.env` file
- Ensure your ESPN account is active

**"Missing required environment variables"**
- Make sure your `.env` file exists and contains all three variables
- Check for typos in variable names
- Ensure no extra spaces around the `=` sign

**"Season has not started yet"**
- This is normal during pre-season or before Week 1
- Wait until at least one week has been completed

**"Failed to generate audio file"**
- Check write permissions in the current directory
- Ensure sufficient disk space
- Verify internet connection for Google TTS service

### Getting Help

If you encounter issues:

1. Check the console output for specific error messages
2. Verify your credentials are correct
3. Ensure all required packages are installed
4. Check your internet connection
5. Try running the script again

## File Structure

```
fantasy-football-recap-generator/
├── recap_generator.py      # Main script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .env                   # Your credentials (create this)
└── recap_week_X.mp3      # Generated audio files
```

## Technical Details

- **ESPN API**: Uses `espn-api` package for data retrieval
- **Text-to-Speech**: Google TTS service via `gtts` package
- **Credential Management**: Secure environment variable loading with `python-dotenv`
- **Error Handling**: Comprehensive try-catch blocks with user-friendly messages
- **Logging**: Detailed logging for debugging and monitoring

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this script.

## License

This project is open source and available under the MIT License.

---

**Happy Fantasy Football Season! 🏈🎉** 