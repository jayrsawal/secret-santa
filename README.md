# Secret Santa

A pythonic way to assign secret santas without human intervention. Requires a gmail oauth credential file. Mappings are logged in `secret_log.json`. Emails will not be sent unless everyone is mapped.

`Usage: secret-santa.py -c <path_to_credentials.json> -t <path_to_token_pickle>`

Note: Token will will safely persist credentials after your first authentication


## secret-santa.json

You may add additional santas in `secret-santa.json` using the following format:
```
{
	<name>: [<email>, <group>]
}
``` 

`name`: Name of the Santa

`email`: Email of the Santa

`group`: Santas in the same group will not be matched together

## secret-santa-email

You may change the email template in this file using the `%(name)s` and `%(target)s` macros.
