#!/usr/bin/env python3
# vim: set fileencoding=ascii :

import argparse
from datetime import datetime
import json
import os
import sys
from types import SimpleNamespace

header = '''<!doctype html>
<html lang="en">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
		<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
		<style>
			:root { --body-bg:#FFFFFF; --body-color:#000000; --footer-color:lightgray; }
			@media(prefers-color-scheme: dark) {
				:root { --body-bg:#000000; --body-color:#FFFFFF; --footer-color:lightgray; }
				.invert { filter:invert(1); }
			}

			body { padding:15px; background: var(--body-bg); color: var(--body-color); }
			h1, h2, .center { text-align:center; }
			.store::before { content:"\\1F6D2 "; }
			.map::before { content:"\\1F4CD "; }
			.phone::before { content:"\\260E\\200D\\FE0F "; }
			.website::before { content:"\\1F5A5 "; }
			.food::before { content:"\\1F37D "; }
			.on_premise::before { content:"\\1F37B "; }
			.social img { height: 2ex; }
			.closed, .no { color:red; }
			.in_planning { color:forestgreen; }
			.closed { color:gray; }
			.separator { color:var(--footer-color); }
			footer { color:var(--footer-color); text-align:center; font-size:8pt; }
			footer a { color:var(--footer-color); }
			section { padding-top: 2ex; }
		</style>
		<title>Beer in Montgomery County, Maryland</title>
	</head>
	<body>
		<h1>Beer in Montgomery County, Maryland</h1>
		<div class="center"><a href="https://thinkmoco.com/made-in-moco/"><img src="logos/drinklocal_mocomade.png" srcset="logos/drinklocal_mocomade.png 1x, logos/drinklocal_mocomade@2x.png 2x" alt="Drink Local. Moco Made." title="#mocomade"></a></div>
'''

google_map = '''		<section>
			<h2>Google Map of Locations</h2>
			<iframe class="d-block mx-auto" src="https://www.google.com/maps/d/u/1/embed?mid=1HcsTMRMiEsDwHCUf9J7_T5jXwnAVGaIZ&z=10&ll=39.14789573526428,-77.2005358102505" width="640" height="480"></iframe>
		</section>
'''

footer = f'''		<footer>
			<hr>
			Made and <a href="https://github.com/gfiumara/mocobeer">open sourced</a> in Gaithersburg by <a href="https://gregfiumara.com">Greg Fiumara</a> and <a href="https://github.com/gfiumara/mocobeer/contributors">contributors</a>.<br>
			Last updated on {datetime.now().strftime("%d %B %Y at %I:%M:%S %p")}.<br>
			&copy; 2018&ndash;{datetime.now().year} <a href="https://gregfiumara.com">Greg Fiumara</a>. <a href="LICENSE">License</a>.
		</footer>
	</body>
</html>
'''

def parse_arguments():
	parser = argparse.ArgumentParser(
	    description = "Generate a static HTML page for moco.beer")
	parser.add_argument('-i', '--input',
	    required = True,
	    metavar = "input.json",
	    dest = "input_file",
	    help = "Input JSON file with location information")
	parser.add_argument('-o', '--output',
	    required = True,
	    dest = "output_file",
	    metavar = "output.html",
	    help = "Output HTML file generated from input JSON")
	parser.add_argument('-f', '--force',
	    dest = "force",
	    action = "store_true")

	args = parser.parse_args()
	if not os.path.exists(args.input_file):
		print(f"Input JSON \"{args.input_file}\" does not exist")
		sys.exit(1)
	if os.path.exists(args.output_file) and not args.force:
		answer = input(f"Output file \"{args.output_file}\" exists. "
		    "Overwrite? [y/n]: ")
		if answer.lower() != 'y' and answer.lower() != "yes":
			sys.exit(0)

	return args

def check_required_location_keys(location):
	required_keys = ["name", "slug", "types"]
	for key in required_keys:
		if location.get(key) is None:
			raise KeyError(f'Property "{key}" not found ({location})')

def separator(counter):
	if counter == 0:
		return ""

	return '<span class="separator"> | </span>'

def phone_format(n):
	str_n = str(n)
	return f"({str_n[0:3]}) {str_n[3:6]}-{str_n[6:]}"

def contains_keys(location, key_list):
	for key in key_list:
		if location.get(key) is not None:
			return True
	return False

def html_for_location(location):
	i = 0
	base_tab = '\t\t\t'
	key = lambda k : location.get(k)
	add_field = lambda counter, existing_html, new_field : (counter + 1, existing_html + separator(counter) + new_field)
	begin_section = lambda counter, existing_html : (0, existing_html + f'\n{base_tab}\t\t<li>')
	end_section = lambda counter, existing_html : (counter, existing_html + '</li>\n')

	location_keys = ["address", "phone_number"]
	social_keys = ["twitter_handle", "facebook_url", "instagram_handle", "yelp_url", "trip_advisor_url"]
	beer_keys = ["untappd_url", "beer_advocate_url", "rate_beer_url", "brewery_db_url"]
	food_keys = ["food", "drink_on_premise"]

	s = f'{base_tab}<dt id="{key("slug")}">'
	if key("open_status") is not None and key("open_status").lower() != "open":
		if "planning" in key("open_status").lower():
			s += f' <span class="in_planning">{key("open_status")}: </span>'
		elif "close" in key("open_status").lower():
			s += f' <span class="closed">{key("open_status")}: </span>'
		else:
			s += f' <span class="status">{key("open_status")}: </span>'
	s += f'{key("name")}</dt>\n{base_tab}<dd>\n{base_tab}\t<ul>'

	# Address and phone number
	if contains_keys(location, location_keys):
		i, s = begin_section(i, s)
		if key("address") is not None and key("google_maps_url") is not None:
			i, s = add_field(i, s, f'<a href="{key("google_maps_url")}" class="map">{key("address")}</a>')
		if key("phone_number") is not None:
			i, s = add_field(i, s,  f'<a href="tel://{key("phone_number")}" class="phone">{phone_format(key("phone_number"))}</a>')
		i, s = end_section(i, s)

	# Social
	if contains_keys(location, social_keys):
		i, s = begin_section(i, s)
		if key("website") is not None:
			i, s = add_field(i, s, f'<a href="{key("website")}" class="social website">Website</a>')
		if key("twitter_handle") is not None:
			i, s = add_field(i, s, f'<a href="https://twitter.com/{key("twitter_handle")}" class="social twitter"><img src="logos/x.svg" alt="X (Twitter) Logo" class="invert"> X (Twitter)</a>')
		if key("facebook_url") is not None:
			i, s = add_field(i, s, f'<a href="{key("facebook_url")}" class="social facebook"><img src="logos/facebook.svg" alt="Facebook Logo"> Facebook</a>')
		if key("facebook_url") is not None:
			i, s = add_field(i, s, f'<a href="https://instagram.com/{key("instagram_handle")}" class="social instagram"><img src="logos/instagram.svg" alt="Instagram Logo" class="invert"> Instagram</a>')
		if key("yelp_url") is not None:
			i, s = add_field(i, s, f'<a href="{key("yelp_url")}" class="social yelp"><img src="logos/yelp.svg" alt="Yelp Logo"> Yelp</a>')
		if key("trip_advisor_url") is not None:
			i, s = add_field(i, s, f'<a href="{key("trip_advisor_url")}" class="social trip_advisor"><img src="logos/trip_advisor.svg" alt="Trip Advisor Logo" class="invert"> Trip Advisor</a>')
		i, s = end_section(i, s)

	# Beer info
	if contains_keys(location, beer_keys):
		i, s = begin_section(i, s)
		if key("untappd_url") is not None:
			i, s = add_field(i, s, f'<a href="{key("untappd_url")}" class="social untappd"><img src="logos/untappd.svg" alt="Untappd Logo"> Untappd</a>')
		if key("beer_advocate_url") is not None:
			i, s = add_field(i, s, f'<a href="{key("beer_advocate_url")}" class="social beer_advocate"><img src="logos/beer_advocate.png" srcset="logos/beer_advocate.png 1x, logos/beer_advocate@2x.png 2x" alt="Beer Advocate Logo"> Beer Advocate</a>')
		if key("ratebeer_url") is not None:
			i, s = add_field(i, s, f'<a href="{key("ratebeer_url")}" class="social ratebeer"><img src="logos/ratebeer.svg" alt="RateBeer Logo"> RateBeer</a>')
		if key("brewerydb_url") is not None:
			i, s = add_field(i, s, f'<a href="{key("brewerydb_url")}" class="social brewerydb"><img src="logos/brewerydb.png" srcset="logos/brewerydb.png 1x, logos/brewerydb@2x.png 2x" alt="BreweryDB Logo"> BreweryDB</a>')
		i, s = end_section(i, s)

	# Online store
	if key("store_url") is not None:
		i, s = begin_section(i, s)
		i, s = add_field(i, s, f'<a href="{key("store_url")}" class="store">Online Store</a>')
		i, s = end_section(i, s)

	# Food, etc.
	if contains_keys(location, food_keys):
		i, s = begin_section(i, s)
		if key("food") is not None:
			if key("food"):
				i, s = add_field(i, s, f'<span class="food">Always serves food</span>')
			else:
				i, s = add_field(i, s, f'<span class="no food">No food service</span>')
		if key("drink_on_premise") is not None:
			if key("drink_on_premise"):
				i, s = add_field(i, s, f'<span class="on_premise">Drink on premise</span>')
			else:
				i, s = add_field(i, s, f'<span class="no on_premise">No drinking on premise</span>')
		i, s = end_section(i, s)

	if key("notes") is not None and len(key("notes")) > 0:
		s += f"{base_tab}\t<li><strong>Notes:</strong>\n"
		s += f"{base_tab}\t\t<ul>\n"
		for note in key("notes"):
			s += f"{base_tab}\t\t\t<li>{note}</li>\n"
		s += f"{base_tab}\t\t</ul></li>\n"

	s += f"{base_tab}\t</ul>\n{base_tab}</dd>\n"
	return s

def html_for_section(location_type, section_title, locations):
	begin_section = lambda slug, caption : f'\t<section>\n\t\t<h2 id="{location_type}">{caption}</h2>\n\t\t<dl>\n'
	end_section = "\t\t</dl>\n\t</section>\n"

	s = begin_section(location_type, section_title)
	for location in locations:
		check_required_location_keys(location)
		if not location_type in location["types"]:
			continue
		s += html_for_location(location)
	s += end_section

	return s

################################################################################

if __name__ == '__main__':
	args = parse_arguments()

	html = header


	with open(args.input_file) as file:
		locations = json.load(file)

	# Sort by name
	locations.sort(key = lambda x : x["name"])

	# Craft breweries
	html += html_for_section(location_type = "craft_brewery",
	    section_title = "Independent Craft Breweries",
	    locations = locations)

	# Chain breweries
	html += html_for_section(location_type = "chain_brewery",
	    section_title = "Chain Breweries",
	    locations = locations)

	# Craft breweries in planning
	html += html_for_section(location_type = "craft_brewery_in_planning",
	    section_title = "Independent Craft Breweries Opening Soon",
	    locations = locations)

	# Bottle shops
	html += html_for_section(location_type = "bottle_shop",
	    section_title = "Notable Bottle Shops",
	    locations = locations)

	# Notable bars
	html += html_for_section(location_type = "bar",
	    section_title = "Notable Bars",
	    locations = locations)

	# Notable restaurants
	html += html_for_section(location_type = "restaurant",
	    section_title = "Notable Restaurants",
	    locations = locations)

	html += google_map
	html += footer

	with open(args.output_file, 'w') as file:
		file.write(html)
