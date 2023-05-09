def build_output_context(session, contexts, parameter):
	out_contexts = []
	for context in contexts:
		out_contexts.append(
		    {
		      "name": session+"/contexts/"+context['name'],
		      "lifespanCount": context['lifespan'],
		      # "parameters": {
		      #   "param": "param value"
		      # }
		    }
		)

	return out_contexts


def build_response(speechlet_response=None, session_attributes=None, output=None, context=None):
	to_return = {
		"speech": output,
		"displayText": output,
		"data": {},
		"contextOut": [],
		"source": "alt",
	}

	if context is not None:
		to_return['outputContexts'] = context

	if type(output) == str:
		output = [output]

	if type(output) == list:
		to_return['speech'] = output[0]
		to_return['displayText'] = output[0]
		to_return["fulfillmentMessages"] = []
		for txt in output:
			to_return["fulfillmentMessages"].append({"text":{"text":[txt]}})
	
	return to_return


def build_telegram_response(output=None, context=None, inline_buttons=None):
	to_return = {
		"speech": output,
		"displayText": output,
		"data": {},
		"contextOut": [],
		"source": "alt",
	}

	if context is not None:
		to_return['outputContexts'] = context

	if type(output) == str:
		output = [output]

	if type(output) == list:
		to_return['speech'] = output[0]
		to_return['displayText'] = output[0]
		to_return["fulfillmentMessages"] = []
		for txt in output:
			if inline_buttons is not None:
				to_return["fulfillmentMessages"].append(
					{
						"payload": {
							"telegram":{
								"text":txt,
								"reply_markup": inline_buttons.to_dict(),
								"parse_mode": "HTML"
							}
						},
						"platform": "TELEGRAM",
						"lang": "en"
					}
				)
			else:
				to_return["fulfillmentMessages"].append(
					{
						"payload": {
							"telegram":{
								"text":txt,
								"parse_mode": "HTML"
							}
						},
						"platform": "TELEGRAM",
						"lang": "en"
					}
				)
	
	return to_return


def build_trigger_response(event_name, params):
	return {
	    "followupEventInput": {
	        "name": event_name, #Name of the event
	        "parameters": params,
	        "languageCode": "en-US"
	    }
	}