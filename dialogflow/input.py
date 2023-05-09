def parse_dialoglow_params(input_json):
	'''
	output array:
	[0] - intent name
	[1] - entities
	[2] - user payload
	[3] - user session
	[4] - current contexts to extract entities
	[5] - action
	[6] - input text
	'''
	if 'result' in input_json:
		return [input_json['result']['action'], input_json['result']['parameters'], None, None]

	if 'outputContexts' in input_json['queryResult']:
		contexts = input_json['queryResult']['outputContexts']
	else:
		contexts = {}

	if 'action' in input_json['queryResult']:
		action = input_json['queryResult']['action']
	else:
		action = ""

	payload = input_json['originalDetectIntentRequest']['payload']
	if 'source' in input_json['originalDetectIntentRequest']:
		payload['source'] = input_json['originalDetectIntentRequest']['source']
	
	return [
		input_json['queryResult']['intent']['displayName'], 
		input_json['queryResult']['parameters'],
		payload,
		input_json['session'],
		contexts,
		action,
		input_json['queryResult']['queryText']
	]


def get_chat_app_user(payload):
	if "source" in payload:
		chat_app = payload['source']

		# Telegram
		if chat_app == "telegram":
			if "callback_query" in payload['data']:
				user = payload['data']['callback_query']['from']
				user['msg_id'] = payload['data']['callback_query']['message']['message_id']
			else:
				user = payload['data']['from']
				user['msg_id'] = payload['data']['message_id']
			user['source_id'] = str(int(user['id']))
			del user['id']
		# Slack
		elif chat_app == "slack":
			user = payload['data']['event']
			user['source_id'] = user['user']
			del user['user']
			del user['client_msg_id']
			del user['event_ts']
			del user['text']
			del user['ts']
			del user['type']
		# Twilio - whatsapp
		elif chat_app == "twilio":
			user = payload['data']
			user['source_id'] = user['From']
			del user['Body']
			del user['MessageSid']
			del user['SmsMessageSid']
			del user['ApiVersion']
			del user['SmsStatus']
			del user['SmsSid']
			del user['NumMedia']
		user['source'] = chat_app
		return user
	else:
		# if source is dialogflow (only for testing purpose)
		return {"source_id": "d1", "source": "dialogflow"}


def get_context_params(in_contexts, intent=None):
	parameters = {}
	for context in in_contexts:
		if 'parameters' in context:
			parameters.update(context['parameters'])

	return parameters


def main(req):
	df_params = parse_dialoglow_params(req)
	user = get_chat_app_user(df_params[2])
	context_params = get_context_params(df_params[4])
	
	return {
		"user": user,
		"query_text": df_params[6],
		"intent": df_params[0],
		"entities": df_params[1],
		"context_params": context_params,
		"params": df_params
	}

    
