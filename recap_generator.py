#!/usr/bin/env python3
"""
Fantasy Football Weekly Recap Generator
... (rest of your docstring) ...
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Tuple, Optional
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import argparse # <-- IMPORT ARGPARSE

# ESPN API import
try:
    from espn_api.football import League
except ImportError:
    print("Error: espn-api package not found. Please install it with: pip install espn-api")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FantasyRecapGenerator:
    """Main class for generating fantasy football weekly recaps."""
    
    # 1. UPDATE THE __init__ METHOD
    def __init__(self, year: Optional[int] = None, week: Optional[int] = None, personality: str = "SVP"):
        """Initialize the generator with credentials and league connection."""
        self.league = None
        self.league_id = None
        self.espn_s2 = None
        self.swid = None
        self.current_week = None
        self.personality = personality
        
        # Store the override arguments from the command line
        self.override_year = year
        self.override_week = week
        
        # Load environment variables
        self._load_credentials()
        
        # Initialize league connection
        self._connect_to_league()
    
    def _load_credentials(self) -> None:
        """Load credentials from .env file."""
        # ... (this method remains exactly the same) ...
        try:
            load_dotenv()
            
            self.league_id = os.getenv('LEAGUE_ID')
            self.espn_s2 = os.getenv('ESPN_S2')
            self.swid = os.getenv('SWID')
            self.gemini_api_key = os.getenv('GEMINI_API_KEY')
            self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
            
            if not all([self.league_id, self.espn_s2, self.swid, self.gemini_api_key, self.elevenlabs_api_key]):
                raise ValueError("Missing required environment variables")
                
            try:
                self.league_id = int(self.league_id)
            except ValueError:
                raise ValueError("LEAGUE_ID must be a valid integer")
            
            # Configure Gemini client
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Initialize ElevenLabs client - use the correct import
            from elevenlabs.text_to_speech.client import TextToSpeechClient
            self.elevenlabs_client = TextToSpeechClient(api_key=self.elevenlabs_api_key)
                
            logger.info("Credentials loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            print("Error: Failed to load credentials from .env file.")
            print("Please ensure your .env file contains LEAGUE_ID, ESPN_S2, SWID, GEMINI_API_KEY, and ELEVENLABS_API_KEY variables.")
            raise e
    
    # 2. UPDATE THE _connect_to_league METHOD
    def _connect_to_league(self) -> None:
        """Establish connection to ESPN fantasy football league."""
        try:
            logger.info("Connecting to ESPN Fantasy Football API...")
            
            # Use the override year if provided, otherwise default to the current year
            target_year = self.override_year if self.override_year else datetime.now().year
            logger.info(f"Connecting to league for the year: {target_year}")

            self.league = League(
                league_id=self.league_id,
                year=target_year, # <-- USE THE TARGET_YEAR VARIABLE
                espn_s2=self.espn_s2,
                swid=self.swid
            )
            
            league_name = self.league.settings.name
            logger.info(f"Successfully connected to league: {league_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to ESPN API: {e}")
            print("Failed to connect to ESPN API. Please check your credentials and internet connection.")
            raise e
    
    # 3. UPDATE THE _get_target_week METHOD
    def _get_target_week(self) -> int:
        """Determine the most recently completed week OR use the override."""
        # If a week was passed in via command-line, use it immediately.
        if self.override_week:
            logger.info(f"MANUAL OVERRIDE: Using week {self.override_week} for recap generation.")
            return self.override_week

        # Otherwise, calculate the week like normal.
        try:
            current_week = self.league.current_week
            target_week = current_week - 1
            
            if target_week < 1:
                raise ValueError("Season has not started yet")
            
            logger.info(f"Current week: {current_week}, Generating recap for week: {target_week}")
            return target_week
            
        except Exception as e:
            logger.error(f"Error determining target week: {e}")
            print("Error: Unable to determine the target week for recap generation.")
            raise e

    # ... (all other methods like _get_week_scoreboard, _analyze_matchups, etc. remain the same) ...
    # (I've removed them from this example for brevity)
    def _get_week_scoreboard(self, week: int) -> List:
        """Fetch the scoreboard for a specific week."""
        try:
            logger.info(f"Fetching scoreboard for week {week}...")
            
            # Get the scoreboard for the specific week
            scoreboard = self.league.scoreboard(week=week)
            
            if not scoreboard:
                raise ValueError(f"No data available for week {week}")
            
            logger.info(f"Successfully fetched {len(scoreboard)} matchups for week {week}")
            return scoreboard
            
        except Exception as e:
            logger.error(f"Failed to fetch scoreboard for week {week}: {e}")
            print(f"Failed to fetch data for week {week}. The week may not be complete yet.")
            raise e
    
    def _analyze_matchups(self, scoreboard: List) -> Tuple[str, dict]:
        """Analyze matchups and generate narrative summary with awards tracking."""
        logger.info("Analyzing matchups and generating narrative...")
        
        # Initialize award tracking variables
        awards = {
            'highest_score': 0.0,
            'highest_scoring_teams': [],
            'lowest_score': float('inf'),
            'lowest_scoring_teams': [],
            'biggest_blowout': 0.0,
            'biggest_blowout_matchup': None,
            'closest_game': float('inf'),
            'closest_game_matchup': None
        }
        
        # Initialize summary text
        summary_parts = []
        
        # Process each matchup
        for matchup in scoreboard:
            home_team = matchup.home_team
            away_team = matchup.away_team
            home_score = round(matchup.home_score, 2)
            away_score = round(matchup.away_score, 2)
            
            # Generate matchup narrative
            matchup_narrative = self._generate_matchup_narrative(
                home_team, away_team, home_score, away_score
            )
            summary_parts.append(matchup_narrative)
            
            # Update awards tracking
            self._update_awards(awards, home_team, away_team, home_score, away_score)
        
        # Generate awards section
        awards_section = self._generate_awards_section(awards)
        summary_parts.append(awards_section)
        
        # Combine all parts
        full_summary = "\n\n".join(summary_parts)
        
        return full_summary, awards
    
    def _generate_recap_with_llm(self, weekly_data: dict) -> str:
        """Generate recap text using Gemini AI with the selected personality."""
        try:
            logger.info(f"Generating recap with {self.personality} personality using Gemini AI...")
            
            # Create the meta-prompt with persona instructions
            persona_instructions = {
                "SVP": "You are Scott Van Pelt from SportsCenter. Use your signature style: be witty, clever, and slightly sarcastic. Reference pop culture, use wordplay, and maintain a conversational tone. Keep it engaging and entertaining.",
                "Chris Berman": "You are Chris Berman from ESPN. Use your signature style: be enthusiastic, use nicknames for players/teams, reference classic rock songs, and maintain high energy throughout. Use phrases like 'WHOOP!' and 'Back, back, back!'",
                "Stuart Scott": "You are Stuart Scott from SportsCenter. Use your signature style: be cool, use urban slang, reference hip-hop culture, and maintain a smooth, confident delivery. Use phrases like 'Boo-yah!' and 'As cool as the other side of the pillow.'"
            }
            
            persona_style = persona_instructions.get(self.personality, persona_instructions["SVP"])
            
            prompt = f"""You are a fantasy football analyst with the personality of {self.personality}.

{persona_style}

Generate a weekly fantasy football recap based on the following data. Make it engaging, entertaining, and true to the personality style requested.

Weekly Data:
{json.dumps(weekly_data, indent=2)}

Requirements:
1. Start with a title: "📊 WEEKLY RECAP FOR WEEK [WEEK] 📊"
2. Include all matchup results in an engaging narrative style
3. End with a "🏆 WEEKLY AWARDS 🏆" section
4. Keep the tone consistent with the requested personality
5. Make it fun and entertaining to read
6. Use emojis and formatting to enhance readability

Generate the recap now:"""

            # Call Gemini API
            response = self.gemini_model.generate_content(prompt)
            generated_text = response.text
            
            logger.info("Successfully generated recap with Gemini AI")
            return generated_text
            
        except Exception as e:
            logger.error(f"Failed to generate recap with LLM: {e}")
            raise e
    
    def _generate_matchup_narrative(self, home_team, away_team, home_score: float, away_score: float) -> str:
        """Generate narrative for a single matchup."""
        home_name = home_team.team_name
        away_name = away_team.team_name
        
        if home_score == away_score:
            # Handle ties
            return f"The matchup between {home_name} and {away_name} was a rare tie, with both teams scoring {home_score} points."
        elif home_score > away_score:
            # Home team wins
            margin = round(home_score - away_score, 2)
            return f"{home_name} triumphed over {away_name} with a final score of {home_score} to {away_score} (margin: {margin} points)."
        else:
            # Away team wins
            margin = round(away_score - home_score, 2)
            return f"{away_name} defeated {home_name} with a final score of {away_score} to {home_score} (margin: {margin} points)."
    
    def _update_awards(self, awards: dict, home_team, away_team, home_score: float, away_score: float) -> None:
        """Update award tracking variables based on current matchup."""
        # Update highest score tracking
        if home_score > awards['highest_score']:
            awards['highest_score'] = home_score
            awards['highest_scoring_teams'] = [home_team.team_name]
        elif home_score == awards['highest_score']:
            awards['highest_scoring_teams'].append(home_team.team_name)
        
        if away_score > awards['highest_score']:
            awards['highest_score'] = away_score
            awards['highest_scoring_teams'] = [away_team.team_name]
        elif away_score == awards['highest_score']:
            if away_team.team_name not in awards['highest_scoring_teams']:
                awards['highest_scoring_teams'].append(away_team.team_name)
        
        # Update lowest score tracking
        if home_score < awards['lowest_score']:
            awards['lowest_score'] = home_score
            awards['lowest_scoring_teams'] = [home_team.team_name]
        elif home_score == awards['lowest_score']:
            awards['lowest_scoring_teams'].append(home_team.team_name)
        
        if away_score < awards['lowest_score']:
            awards['lowest_score'] = away_score
            awards['lowest_scoring_teams'] = [away_team.team_name]
        elif away_score == awards['lowest_score']:
            if away_team.team_name not in awards['lowest_scoring_teams']:
                awards['lowest_scoring_teams'].append(away_team.team_name)
        
        # Update blowout tracking (excluding ties)
        if home_score != away_score:
            margin = abs(home_score - away_score)
            if margin > awards['biggest_blowout']:
                awards['biggest_blowout'] = margin
                awards['biggest_blowout_matchup'] = (home_team.team_name, away_team.team_name, home_score, away_score)
            
            # Update closest game tracking
            if margin < awards['closest_game']:
                awards['closest_game'] = margin
                awards['closest_game_matchup'] = (home_team.team_name, away_team.team_name, home_score, away_score)
    
    def _generate_awards_section(self, awards: dict) -> str:
        """Generate the weekly awards section."""
        awards_text = ["🏆 WEEKLY AWARDS 🏆"]
        
        # Manager of the Week
        if len(awards['highest_scoring_teams']) == 1:
            awards_text.append(f"Manager of the Week: {awards['highest_scoring_teams'][0]} with an incredible {awards['highest_score']} points!")
        else:
            teams_str = " and ".join(awards['highest_scoring_teams'])
            awards_text.append(f"Manager of the Week: {teams_str} share the honor, both putting up {awards['highest_score']} points!")
        
        # Blowout of the Week
        if awards['biggest_blowout_matchup']:
            winner, loser, winner_score, loser_score = awards['biggest_blowout_matchup']
            awards_text.append(f"Blowout of the Week: {winner} dominated {loser} by {awards['biggest_blowout']} points ({winner_score} to {loser_score})!")
        
        # Nail-Biter of the Week
        if awards['closest_game_matchup']:
            team1, team2, score1, score2 = awards['closest_game_matchup']
            awards_text.append(f"Nail-Biter of the Week: {team1} vs {team2} was decided by just {awards['closest_game']} points!")
        
        # Sad Trombone Award
        if len(awards['lowest_scoring_teams']) == 1:
            awards_text.append(f"Sad Trombone Award: {awards['lowest_scoring_teams'][0]} with only {awards['lowest_score']} points. Better luck next week!")
        else:
            teams_str = " and ".join(awards['lowest_scoring_teams'])
            awards_text.append(f"Sad Trombone Award: {teams_str} both struggled with only {awards['lowest_score']} points each.")
        
        return "\n".join(awards_text)
    
    def _convert_to_audio_elevenlabs(self, text: str, week: int) -> str:
        """Convert text summary to MP3 audio file using ElevenLabs."""
        try:
            logger.info("Converting text to speech using ElevenLabs...")
            
            # Create filename
            filename = f"recap_week_{week}.mp3"
            
            # Use ElevenLabs to generate audio (using "Adam" voice)
            # Use the convert method with proper parameters
            audio_data = self.elevenlabs_client.convert(
                text=text,
                voice_id="Adam",  # Note: voice_id not voice
                model_id="eleven_monolingual_v1"
            )
            
            # Save the audio data to file
            with open(filename, "wb") as f:
                f.write(audio_data)
            
            logger.info(f"Audio file saved successfully: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to convert text to audio with ElevenLabs: {e}")
            print(f"Error: Failed to generate audio file: {e}")
            raise e
    
    def generate_weekly_recap(self) -> None:
        """Main method to generate the weekly recap."""
        try:
            logger.info("Starting weekly recap generation...")
            
            # Get target week
            target_week = self._get_target_week()
            
            # Get scoreboard data
            scoreboard = self._get_week_scoreboard(target_week)
            
            # Generate raw data structure for LLM
            raw_data = self._analyze_matchups(scoreboard)
            summary, awards = raw_data
            
            # Create structured data for LLM
            weekly_data = {
                "week": target_week,
                "summary": summary,
                "awards": awards
            }
            
            # Generate enhanced recap with LLM
            enhanced_summary = self._generate_recap_with_llm(weekly_data)
            
            # Print summary to console
            print("\n" + "="*60)
            print("FANTASY FOOTBALL WEEKLY RECAP")
            print("="*60)
            print(enhanced_summary)
            print("="*60)
            
            # Convert to audio using ElevenLabs
            audio_filename = self._convert_to_audio_elevenlabs(enhanced_summary, target_week)
            
            # Success message
            print(f"\n✅ Successfully generated audio recap: {audio_filename}")
            print(f"📁 File saved in: {os.getcwd()}")

            # Return the results so the API can use them
            return enhanced_summary, audio_filename
            
        except Exception as e:
            logger.error(f"Unexpected error during recap generation: {e}")
            print(f"An unexpected error occurred: {e}")
            # Instead of exiting, raise the exception so the API can catch it
            raise e

def main():
    """Main entry point for the script."""
    # Add Argument Parsing
    parser = argparse.ArgumentParser(description="Generate a weekly fantasy football recap.")
    parser.add_argument("--year", type=int, help="The year to generate the recap for (e.g., 2024).")
    parser.add_argument("--week", type=int, help="The week to generate the recap for.")
    parser.add_argument("--personality", type=str, default="SVP", choices=["SVP", "Chris Berman", "Stuart Scott"], 
                       help="The personality style for the recap (default: SVP)")
    args = parser.parse_args()

    try:
        print("🎯 Fantasy Football Weekly Recap Generator")
        print(f"Personality: {args.personality}")
        print("Loading credentials and connecting to ESPN...")
        
        # Pass the arguments to the generator
        generator = FantasyRecapGenerator(year=args.year, week=args.week, personality=args.personality)
        
        # Generate recap
        generator.generate_weekly_recap()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()