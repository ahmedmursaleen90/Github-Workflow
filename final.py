"""
Weather App — Flask web application
Uses Open-Meteo (free, no API key required) for real weather data.
Run: python app.py
Open: http://localhost:5000
"""

from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

HTML = u"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skye - Weather</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --sky: #0e1b2e; --sky-mid: #152640; --sky-glow: #1e3a5f;
    --accent: #60b8ff; --accent-warm: #ffd080;
    --text: #e8f4ff; --text-muted: #7ba7cc;
    --card-bg: rgba(255,255,255,0.06); --card-border: rgba(255,255,255,0.1);
    --radius: 20px;
  }
  body { min-height: 100vh; background: var(--sky); font-family: 'DM Sans', sans-serif; color: var(--text); overflow-x: hidden; }
  .wrap { position: relative; z-index: 1; max-width: 860px; margin: 0 auto; padding: 40px 24px 60px; }
  header { text-align: center; margin-bottom: 40px; }
  .brand { font-family: 'DM Serif Display', serif; font-style: italic; font-size: 2rem; color: var(--accent); }
  .tagline { font-size: 0.8rem; color: var(--text-muted); letter-spacing: 0.12em; text-transform: uppercase; margin-top: 4px; }
  .search-row { display: flex; gap: 10px; max-width: 480px; margin: 0 auto 40px; }
  .search-row input { flex: 1; background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 50px; padding: 13px 22px; color: var(--text); font-family: inherit; font-size: 0.95rem; outline: none; transition: border-color 0.2s; }
  .search-row input::placeholder { color: var(--text-muted); }
  .search-row input:focus { border-color: var(--accent); }
  .search-row button { background: var(--accent); color: #0e1b2e; border: none; border-radius: 50px; padding: 13px 26px; font-family: inherit; font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: opacity 0.2s; white-space: nowrap; }
  .search-row button:hover { opacity: 0.88; }
  #result { display: none; }
  .hero-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--radius); padding: 36px 40px 32px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; gap: 24px; }
  .city-name { font-family: 'DM Serif Display', serif; font-size: 2.2rem; line-height: 1.1; margin-bottom: 6px; }
  .city-meta { font-size: 0.82rem; color: var(--text-muted); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 20px; }
  .temp-big { font-family: 'DM Serif Display', serif; font-size: 5rem; line-height: 1; color: var(--accent-warm); }
  .temp-big sup { font-size: 2rem; vertical-align: super; color: var(--text-muted); }
  .condition-label { font-size: 1.05rem; color: var(--text-muted); margin-top: 8px; }
  .hero-right { text-align: center; }
  .weather-icon { font-size: 6rem; line-height: 1; display: block; margin-bottom: 4px; }
  .feels-like { font-size: 0.82rem; color: var(--text-muted); }
  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
  .stat-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 18px 16px; text-align: center; }
  .stat-icon { font-size: 1.4rem; margin-bottom: 6px; display: block; }
  .stat-label { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
  .stat-val { font-size: 1.25rem; font-weight: 500; }
  .forecast-row { display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; }
  .fc-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 14px 8px; text-align: center; transition: border-color 0.2s; }
  .fc-card:hover { border-color: var(--accent); }
  .fc-day { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
  .fc-icon { font-size: 1.6rem; display: block; margin-bottom: 6px; }
  .fc-hi { font-size: 1rem; font-weight: 500; }
  .fc-lo { font-size: 0.8rem; color: var(--text-muted); margin-top: 2px; }
  .error-msg { text-align: center; padding: 32px; color: #ff7b7b; font-size: 1rem; display: none; }
  .loading { text-align: center; padding: 60px 0; color: var(--text-muted); font-size: 1rem; display: none; }
  .loading span { display: inline-block; animation: pulse 1.4s ease-in-out infinite; }
  @keyframes pulse { 0%,100% { opacity: 0.4; } 50% { opacity: 1; } }
  @media (max-width: 640px) {
    .hero-card { flex-direction: column; text-align: center; padding: 28px 24px; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .forecast-row { grid-template-columns: repeat(4, 1fr); }
    .temp-big { font-size: 3.5rem; }
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="brand">Skye</div>
    <div class="tagline">Weather, beautifully simple</div>
  </header>
  <div class="search-row">
    <input type="text" id="cityInput" placeholder="Enter city name..." onkeydown="if(event.key==='Enter')search()">
    <button onclick="search()">Search</button>
  </div>
  <div class="loading" id="loading"><span>Fetching weather data...</span></div>
  <div class="error-msg" id="errMsg"></div>
  <div id="result">
    <div class="hero-card">
      <div class="hero-left">
        <div class="city-name" id="cityDisplay"></div>
        <div class="city-meta" id="cityMeta"></div>
        <div class="temp-big" id="tempDisplay"></div>
        <div class="condition-label" id="conditionDisplay"></div>
      </div>
      <div class="hero-right">
        <span class="weather-icon" id="weatherIcon"></span>
        <div class="feels-like" id="feelsLike"></div>
      </div>
    </div>
    <div class="stats-grid">
      <div class="stat-card"><span class="stat-icon">&#128167;</span><div class="stat-label">Humidity</div><div class="stat-val" id="humidity"></div></div>
      <div class="stat-card"><span class="stat-icon">&#128168;</span><div class="stat-label">Wind</div><div class="stat-val" id="wind"></div></div>
      <div class="stat-card"><span class="stat-icon">&#127777;</span><div class="stat-label">Pressure</div><div class="stat-val" id="pressure"></div></div>
      <div class="stat-card"><span class="stat-icon">&#128065;</span><div class="stat-label">Visibility</div><div class="stat-val" id="visibility"></div></div>
    </div>
    <div class="forecast-row" id="forecastRow"></div>
  </div>
</div>
<script>
var WMO = {
  0:['&#9728;','Clear Sky'],
  1:['&#127780;','Mostly Clear'],
  2:['&#9925;','Partly Cloudy'],
  3:['&#9729;','Overcast'],
  45:['&#127787;','Foggy'],
  48:['&#127787;','Icy Fog'],
  51:['&#127746;','Light Drizzle'],
  53:['&#127783;','Drizzle'],
  55:['&#127783;','Heavy Drizzle'],
  61:['&#127746;','Light Rain'],
  63:['&#127783;','Rain'],
  65:['&#127783;','Heavy Rain'],
  71:['&#127784;','Light Snow'],
  73:['&#10052;','Snow'],
  75:['&#10052;','Heavy Snow'],
  80:['&#127746;','Showers'],
  81:['&#127783;','Heavy Showers'],
  82:['&#9928;','Violent Showers'],
  95:['&#9928;','Thunderstorm'],
  96:['&#9928;','Hail Storm'],
  99:['&#9928;','Heavy Hail']
};
function getW(code){ return WMO[code]||['&#127777;','Unknown']; }
function dayName(s,i){
  if(i===0)return'Today';
  var d=new Date(s);
  return d.toLocaleDateString('en-US',{weekday:'short'});
}
async function search(){
  var city=document.getElementById('cityInput').value.trim();
  if(!city)return;
  document.getElementById('result').style.display='none';
  document.getElementById('errMsg').style.display='none';
  document.getElementById('loading').style.display='block';
  try{
    var res=await fetch('/weather?city='+encodeURIComponent(city));
    var data=await res.json();
    document.getElementById('loading').style.display='none';
    if(data.error){
      document.getElementById('errMsg').textContent=data.error;
      document.getElementById('errMsg').style.display='block';
      return;
    }
    var w=getW(data.current.weather_code);
    document.getElementById('cityDisplay').textContent=data.city;
    document.getElementById('cityMeta').textContent=data.country+' - '+data.timezone;
    document.getElementById('tempDisplay').innerHTML=Math.round(data.current.temperature_2m)+'<sup>°C</sup>';
    document.getElementById('conditionDisplay').textContent=w[1];
    document.getElementById('weatherIcon').innerHTML=w[0];
    document.getElementById('feelsLike').textContent='Feels like '+Math.round(data.current.apparent_temperature)+'°C';
    document.getElementById('humidity').textContent=data.current.relative_humidity_2m+'%';
    document.getElementById('wind').textContent=Math.round(data.current.wind_speed_10m)+' km/h';
    document.getElementById('pressure').textContent=data.current.surface_pressure+' hPa';
    document.getElementById('visibility').textContent=(data.hourly.visibility[0]/1000).toFixed(1)+' km';
    var fr=document.getElementById('forecastRow');
    fr.innerHTML='';
    for(var i=0;i<7;i++){
      var fw=getW(data.daily.weather_code[i]);
      fr.innerHTML+='<div class="fc-card"><div class="fc-day">'+dayName(data.daily.time[i],i)+'</div><span class="fc-icon">'+fw[0]+'</span><div class="fc-hi">'+Math.round(data.daily.temperature_2m_max[i])+'°</div><div class="fc-lo">'+Math.round(data.daily.temperature_2m_min[i])+'°</div></div>';
    }
    document.getElementById('result').style.display='block';
  }catch(e){
    document.getElementById('loading').style.display='none';
    document.getElementById('errMsg').textContent='Network error. Please check your internet.';
    document.getElementById('errMsg').style.display='block';
  }
}
window.onload=function(){ document.getElementById('cityInput').value='Karachi'; search(); };
</script>
</body>
</html>"""


def geocode(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    r = requests.get(url, params={"name": city, "count": 1, "language": "en"}, timeout=8)
    data = r.json()
    if not data.get("results"):
        return None
    loc = data["results"][0]
    return {
        "lat": loc["latitude"],
        "lon": loc["longitude"],
        "city": loc.get("name", city),
        "country": loc.get("country", ""),
        "timezone": loc.get("timezone", "UTC"),
    }


def fetch_weather(lat, lon, timezone):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": timezone,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,surface_pressure,wind_speed_10m",
        "hourly": "visibility",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "forecast_days": 7,
    }
    r = requests.get(url, params=params, timeout=8)
    return r.json()


@app.route("/")
def index():
    return Response(HTML, content_type="text/html; charset=utf-8")


@app.route("/weather")
def weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Please enter a city name."})
    try:
        geo = geocode(city)
        if not geo:
            return jsonify({"error": 'City "' + city + '" not found.'})
        data = fetch_weather(geo["lat"], geo["lon"], geo["timezone"])
        data["city"] = geo["city"]
        data["country"] = geo["country"]
        data["timezone"] = geo["timezone"]
        return jsonify(data)
    except requests.Timeout:
        return jsonify({"error": "Request timed out. Check internet connection."})
    except Exception as e:
        return jsonify({"error": "Something went wrong: " + str(e)})


if __name__ == "__main__":
    print("")
    print("  Skye Weather App")
    print("  Open browser: http://localhost:5000")
    print("  Press Ctrl+C to stop")
    print("")
    app.run(debug=False, host="0.0.0.0", port=5000)