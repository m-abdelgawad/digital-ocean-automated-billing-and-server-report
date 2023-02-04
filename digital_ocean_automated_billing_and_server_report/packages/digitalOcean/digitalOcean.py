import json
import requests
from datetime import datetime, timedelta


class DigitalOcean:
    """
    Integrate with DigitalOcean API and retrieve the following information:
        - Month to date usage
        - Account balance
        - Month to date balance
        - Last invoice
        - Last payment
        - Droplet specs:
            - ID
            - Name
            - vCPUs
            - Memory
            - Disk
            - Monthly Price
            - IP
        - Max CPU in a time interval
        - CPU usage data in a time interval

    Available Methods:
        get_balance()
        get_last_invoice()
        get_last_payment()
        get_droplet_specs(droplet_name)
        get_cpu_metrics(days_count, host_id)

    """
    def __init__(self, bearer_token):
        self.headers = None
        self._setup_token(bearer_token=bearer_token)
        self._set_headers()
        self.api_url = 'https://api.digitalocean.com/v2/'

    def _setup_token(self, bearer_token):
        self.token = 'Bearer ' + bearer_token

    def _set_headers(self):
        self.headers = {
            'Authorization': self.token,
        }

    def _build_api_url(self, endpoint):
        # Add a forward slash the base API url doesn't end with a forward slash
        if self.api_url[-1] != '/':
            self.api_url += '/'

        # Remove the forward slash if the endpoint starts with a forward slash
        if endpoint[0] == '/':
            endpoint = endpoint[1:]

        # Join the base API URL and the endpoint; then return them
        return self.api_url + endpoint

    @staticmethod
    def _format_str_date(input_date, current_format, target_format):
        return datetime.strptime(input_date, current_format).strftime(
            target_format)

    def _reformat_date(self, input_date):
        """
        Timestamps are formatted according to ISO8601, e.g. 2023-02-03T06:22:53Z
        The T separates date and time, the Z stands for "zulu time", i.e. UTC.
        The correct strptime format code would be '%Y-%m-%dT%H:%M:%S%z'
        :param input_date: The date to be converted
        :return: The formatted date
        """
        input_format = '%Y-%m-%dT%H:%M:%S%z'
        return datetime.strptime(input_date, input_format).strftime(
            '%d %b %Y %H:%M')

    def _get_today_date(self):
        today = datetime.now()
        today_epoch = self._datetime_to_epoch(datetime_object=today)
        return today_epoch

    def _get_past_date(self, days_count):
        tday_date = datetime.now()
        past_date = timedelta(days=days_count)
        past_date = tday_date - past_date
        past_date_epoch = self._datetime_to_epoch(datetime_object=past_date)
        return past_date_epoch

    @staticmethod
    def _datetime_to_epoch(datetime_object):
        epoch = datetime.utcfromtimestamp(0)
        return int((datetime_object.replace(microsecond=0) - epoch).total_seconds())

    @staticmethod
    def _epoch_to_datetime(epoch_date, output_format):
        return datetime.fromtimestamp(epoch_date).strftime(output_format)

    def get_balance(self):
        """
        Get your balance details. In Digital Ocean API, -ve implies excess
        payment and +ve implies owed charges. This is confusing; thus, I
        reverse the signs of the API output.

        :return: a dictionary with the following keys:
            month_to_date_usage: Amount used in the current billing period as
                of the generated_at time.
            account_balance: Current balance of the customer's most recent
                billing activity. Does not reflect month_to_date_usage.
            month_to_date_balance: Balance as of the generated_at time. This
                value includes the account_balance and month_to_date_usage.
            generated_at: The time at which balances were most recently
                generated.
        """
        api_url = self._build_api_url('/customers/my/balance')

        response = requests.request("GET", api_url, headers=self.headers)

        response_dict = json.loads(response.text)

        # Fix formats of month_to_date_balance, account_balance and generated_at
        response_dict['month_to_date_balance'] = \
            float(response_dict['month_to_date_balance']) * -1
        response_dict['account_balance'] = \
            float(response_dict['account_balance']) * -1
        response_dict['generated_at'] = self._reformat_date(
            response_dict['generated_at']
        )
        return response_dict

    def get_last_invoice(self):
        """
        Get the last invoice

        :return: A dictionary with the following keys:
            invoice_uuid: The ID of the invoice.
            amount: The amount of the invoice.
            invoice_period: The period of the invoice.
        """
        api_url = self._build_api_url('/customers/my/invoices')

        response = requests.request("GET", api_url, headers=self.headers)

        response_dict = json.loads(response.text)['invoices'][0]

        # Reformat the invoice date
        response_dict['invoice_period'] = self._format_str_date(
            input_date=response_dict['invoice_period'],
            current_format='%Y-%m',
            target_format='%b %Y'
        )
        return response_dict

    def get_last_payment(self):
        """
        Get the last payment details.

        :return: A dictionary with the following keys:
            description,
            amount,
            date,
            type,
            receipt_id
        """
        api_url = self._build_api_url('/customers/my/billing_history')

        response = requests.request("GET", api_url, headers=self.headers)

        response_dict = json.loads(response.text)

        # Return the latest payment dictionary
        for payment_dict in response_dict['billing_history']:
            if payment_dict['type'] == 'Payment':
                # Fix the date
                payment_dict['date'] = self._reformat_date(
                    payment_dict['date']
                )
                return payment_dict

    def get_droplet_specs(self, droplet_name):
        """
        Get the technical specs for a droplet.

        :return: A dictionary with the following keys:
            id,
            name,
            vcpus,
            memory,
            disk,
            price_monthly,
            ip
        """
        api_url = self._build_api_url('/droplets')

        response = requests.request("GET", api_url, headers=self.headers)

        response_dict = json.loads(response.text)

        droplet_dict = {}

        for droplet in response_dict['droplets']:
            if droplet['name'] == droplet_name:
                droplet_dict = droplet
                break

        droplet_specs_dict = {
            'id': droplet_dict['id'],
            'name': droplet_dict['name'],
            'vcpus': droplet_dict['vcpus'],
            'memory': droplet_dict['memory'],
            'disk': droplet_dict['disk'],
            'price_monthly': droplet_dict['size']['price_monthly'],
            'ip': droplet_dict['networks']['v4'][0]['ip_address'],
        }

        return droplet_specs_dict

    def get_cpu_metrics(self, host_id, days_count):
        """
        Get the CPU metrics of a droplet for the last week
        :return:
        """

        # Prepare the dates
        start_date = self._get_past_date(days_count=days_count)
        end_date = self._get_today_date()

        api_url = self._build_api_url('monitoring/metrics/droplet/cpu')

        # Add extra headers
        params = dict()
        params['host_id'] = str(host_id)
        params['start'] = str(start_date)
        params['end'] = str(end_date)

        response = requests.request(
            "GET", api_url, headers=self.headers, params=params
        )

        response_dict = json.loads(response.text)

        # results_dict = {'timestamp': {'ideal': ###, ....}, }

        results_dict = dict()

        for bucket in response_dict['data']['result']:
            mode = bucket['metric']['mode']
            for value_list in bucket['values']:
                timestamp = self._epoch_to_datetime(value_list[0], '%Y-%m-%d %H:%M')
                value = value_list[1]
                if timestamp not in results_dict:
                    results_dict[timestamp] = {}
                    results_dict[timestamp][mode] = value
                else:
                    results_dict[timestamp][mode] = value

        cpu_labels = []
        cpu_data = []

        for timestamp in results_dict:
            user = float(results_dict[timestamp]['user'])
            nice = float(results_dict[timestamp]['nice'])
            system = float(results_dict[timestamp]['system'])
            idle = float(results_dict[timestamp]['idle'])
            iowait = float(results_dict[timestamp]['iowait'])
            irq = float(results_dict[timestamp]['irq'])
            softirq = float(results_dict[timestamp]['softirq'])
            steal = float(results_dict[timestamp]['steal'])
            total = user + nice + system + idle + iowait + irq + softirq + steal
            idle = idle + iowait
            usage = total - idle
            cpu_util = round(usage*100/total, 2)
            cpu_labels.append(timestamp)
            cpu_data.append(cpu_util)

        max_cpu_percent = max(cpu_data)
        max_cpu_index = cpu_data.index(max_cpu_percent)
        max_cpu_time = cpu_labels[max_cpu_index]

        output_dict = {
            'max_cpu_percent': max_cpu_percent,
            'max_cpu_time': max_cpu_time,
            'cpu_labels': cpu_labels,
            'cpu_data': cpu_data
        }

        return output_dict
