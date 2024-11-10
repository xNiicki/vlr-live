from flask import Flask, jsonify
from flask_cors import CORS
from flask_caching import Cache
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# Configure caching
cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 15
}
app.config.from_mapping(cache_config)
cache = Cache(app)

class VLRScraper:
    def __init__(self):
        self.base_url = "https://www.vlr.gg"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_page(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_stage_and_event(self, event_string):
        parts = re.split(r'\t+\n\t+', event_string)
        parts = [re.sub(r'\s+', ' ', part).strip() for part in parts]
        stage = parts[0] if parts else ""
        event_name = parts[1] if len(parts) > 1 else ""
        return stage, event_name

    def get_matches(self):
        soup = self.get_page(f"{self.base_url}/matches")
        if not soup:
            return []

        matches = []
        match_elements = soup.select('a.wf-module-item.match-item')
        for match in match_elements:
            try:
                href = match.get('href', '')
                match_id = re.search(r'/(\d+)/', href)
                match_id = match_id.group(1) if match_id else None

                time = match.select_one('.match-item-time').text.strip()
                teams = match.select('.match-item-vs-team-name .text-of')
                team1 = teams[0].text.strip() if len(teams) > 0 else "TBD"
                team2 = teams[1].text.strip() if len(teams) > 1 else "TBD"
                
                team1_flag = match.select_one('.match-item-vs-team:nth-of-type(1) .flag')
                team2_flag = match.select_one('.match-item-vs-team:nth-of-type(2) .flag')
                team1_flag_class = team1_flag['class'][-1] if team1_flag else None
                team2_flag_class = team2_flag['class'][-1] if team2_flag else None
                
                event_element = match.select_one('.match-item-event')
                event_text = event_element.text.strip() if event_element else "Unknown Event"
                stage, event = self.extract_stage_and_event(event_text)
                
                # Check if the match is live
                live_element = match.select_one('.match-item-eta .ml.mod-live')
                eta_text = "LIVE" if live_element else ""
                
                if not eta_text:
                    eta = match.select_one('.ml-eta')
                    eta_text = eta.text.strip() if eta else ""
                
                scores = match.select('.match-item-vs-team-score')
                team1_score = scores[0].text.strip() if len(scores) > 0 else "0"
                team2_score = scores[1].text.strip() if len(scores) > 1 else "0"

                matches.append({
                    'match_id': match_id,
                    'time': time,
                    'team1': team1,
                    'team2': team2,
                    'team1_flag': team1_flag_class,
                    'team2_flag': team2_flag_class,
                    'stage': stage,
                    'event': event,
                    'eta': eta_text,
                    'team1_score': team1_score,
                    'team2_score': team2_score
                })
            except Exception as e:
                print(f"Error parsing match: {e}")

        return matches

    
    def clean_text(self, text):
        # Remove tabs and newlines, and strip extra whitespace
        return re.sub(r'\s+', ' ', text).strip()

    def get_match_details(self, match_id):
        soup = self.get_page(f"{self.base_url}/{match_id}")
        if not soup:
            return None

        try:
            match_details = {}

            # Event and stage
                # Event and stage
            event_element = soup.select_one('.match-header-event')
            if event_element:
                stage_element = event_element.select_one('.match-header-event-series')
                match_details['stage'] = self.clean_text(stage_element.text) if stage_element else "Unknown Stage"
                event_name = event_element.select_one('div')
                match_details['event'] = self.clean_text(event_name.text) if event_name else "Unknown Event"
                
                # Remove the content of match-header-event-series
                series_element = event_element.select_one('.match-header-event-series')
                if series_element:
                    series_element.decompose()
                
                # Get the cleaned event name without the series information
                match_details['event'] = self.clean_text(event_element.text)
                print(match_details['event'])


            # ETA or status
            eta_element = soup.select_one('.match-header-vs-note .mod-live')
            match_details['status'] = self.clean_text(eta_element.text) if eta_element else "Upcoming"

            # Teams, logos, and scores
            teams = soup.select('.match-header-link')
            for i, team in enumerate(teams[:2], 1):
                team_name = team.select_one('.wf-title-med')
                team_logo = team.select_one('img')
                match_details[f'team{i}'] = self.clean_text(team_name.text) if team_name else f"Team {i}"
                match_details[f'team{i}_logo'] = team_logo['src'] if team_logo and 'src' in team_logo.attrs else None

            score_elements = soup.select('.match-header-vs-score .js-spoiler span')
            match_details['team1_score'] = self.clean_text(score_elements[0].text) if len(score_elements) > 0 else "0"
            match_details['team2_score'] = self.clean_text(score_elements[2].text) if len(score_elements) > 1 else "0"

                # Maps
            match_details['maps'] = []
            map_elements = soup.select('.vm-stats-game')
            for map_element in map_elements:
                map_name = map_element.select_one('.map')
                map_scores = map_element.select('.score')
                if map_name:
                    map_text = self.clean_text(map_name.text)
                    map_parts = map_text.split()
                    
                    map_info = {
                        'name': map_parts[0],  # The first part is always the map name
                        'pick': 'PICK' if 'PICK' in map_parts else '',
                        'time': map_parts[-1] if map_parts[-1] != 'PICK' else '',
                        'team1_score': self.clean_text(map_scores[0].text) if len(map_scores) > 0 else "0",
                        'team2_score': self.clean_text(map_scores[1].text) if len(map_scores) > 1 else "0"
                    }
                    match_details['maps'].append(map_info)

            # Streams
            match_details['streams'] = []
            stream_elements = soup.select('.match-streams-container .match-streams-btn')
            for stream in stream_elements:
                stream_name = stream.select_one('span')
                stream_link = stream.select_one('.match-streams-btn-external')
                if stream_name and stream_link and 'href' in stream_link.attrs:
                    match_details['streams'].append({
                        'name': self.clean_text(stream_name.text),
                        'link': stream_link['href']
                    })

            return match_details

        except Exception as e:
            print(f"Error parsing match details: {e}")
            return None




@app.route('/matches', methods=['GET'])
@cache.cached(timeout=15)  # Cache this route for 15 seconds
def get_matches_json():
    scraper = VLRScraper()
    matches = scraper.get_matches()
    return jsonify(matches)

@app.route('/match/<match_id>', methods=['GET'])
@cache.cached(timeout=15)  # Cache this route for 15 seconds
def get_match_details(match_id):
    scraper = VLRScraper()
    match_details = scraper.get_match_details(match_id)
    if match_details:
        return jsonify(match_details)
    else:
        return jsonify({"error": "Match not found or error occurred"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9091)