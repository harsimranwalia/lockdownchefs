import json
from flask import Flask, jsonify, request
from df_webhook import lambda_handler
from df_intent_handlers import mailchimp_user_subscribe
from mailchimp.main import mailchimp_callback_data_to_json
from config import APP_SECRET

app = Flask(__name__)
app.secret_key = APP_SECRET


@app.route('/', methods=['GET', 'POST'])
def dialogflow():
	if request.method == 'POST':
		resp = lambda_handler(json.loads(request.data), None)
		return jsonify(resp)
	if request.method == 'GET':
		test_event = "scheduler"
		if test_event == "scheduler":
			# cloudwatch scheduled event
			cw_event = {
				# "devtest": True,
				"source_id": "307705210",
				"version": "0",
				"id": "53dc4d37-cffa-4f76-80c9-8b7d4a4d2eaa",
				"detail-type": "Scheduled Event",
				"source": "aws.events",
				"account": "123456789012",
				"time": "2015-10-08T16:53:06Z",
				"region": "us-east-1",
				"resources": [
					"arn:aws:events:us-east-1:123456789012:rule/my-scheduled-rule"
				],
				"detail": {}
			}
		elif test_event == "df_webhook":
			cw_event = {'user': {'last_name': 'Walia', 'language_code': 'en', 'first_name': 'Harsimran', 'source_id': '307705210', 'source': 'telegram'}, 'query_text': 'Netherlands', 'intent': 'breakfast_option', 'entities': {'geo-country': 'Netherlands', 'geo-city': ''}, 'context_params': {'geo-country': 'Netherlands', 'geo-country.original': 'Netherlands', 'geo-city': '', 'geo-city.original': '', 'no-input': 0.0, 'no-match': 0.0}, 'params': ['location_personalisation', {'geo-country': 'Netherlands', 'geo-city': ''}, {'data': {'chat': {'id': '307705210', 'type': 'private'}, 'message_id': 59.0, 'text': 'Netherlands', 'date': 1589300699.0, 'from': {'last_name': 'Walia', 'id': 307705210.0, 'language_code': 'en', 'first_name': 'Harsimran', 'source_id': '307705210', 'source': 'telegram'}}, 'source': 'telegram'}, 'projects/lockdown-chefs/agent/sessions/1b6321e7-cf18-3e7e-ab81-b7a8d95eb549', [{'name': 'projects/lockdown-chefs/agent/sessions/1b6321e7-cf18-3e7e-ab81-b7a8d95eb549/contexts/user_pref', 'lifespanCount': 5, 'parameters': {'geo-country': 'Netherlands', 'geo-country.original': 'Netherlands', 'geo-city': '', 'geo-city.original': ''}}, {'name': 'projects/lockdown-chefs/agent/sessions/1b6321e7-cf18-3e7e-ab81-b7a8d95eb549/contexts/city_name', 'lifespanCount': 4, 'parameters': {'geo-country': 'Netherlands', 'geo-country.original': 'Netherlands', 'geo-city': '', 'geo-city.original': ''}}, {'name': 'projects/lockdown-chefs/agent/sessions/1b6321e7-cf18-3e7e-ab81-b7a8d95eb549/contexts/welcome', 'lifespanCount': 4, 'parameters': {'geo-country': 'Netherlands', 'geo-country.original': 'Netherlands', 'geo-city': '', 'geo-city.original': ''}}, {'name': 'projects/lockdown-chefs/agent/sessions/1b6321e7-cf18-3e7e-ab81-b7a8d95eb549/contexts/__system_counters__', 'parameters': {'no-input': 0.0, 'no-match': 0.0, 'geo-country': 'Netherlands', 'geo-country.original': 'Netherlands', 'geo-city': '', 'geo-city.original': ''}}], '', 'Netherlands']}
		lambda_handler(cw_event, None)
		return "Hello World!"

@app.route('/mailchimp', methods=['GET', 'POST'])
def mailchimp():
	if request.method == 'GET':
		return {}

	if request.method == 'POST':
		data = request.form
		data = mailchimp_callback_data_to_json(data)
		mailchimp_user_subscribe(data)

if __name__ == '__main__':
	app.run(host="0.0.0.0", debug=True)
	# https://7acm7hlt65.execute-api.ap-south-1.amazonaws.com/prod/lc


