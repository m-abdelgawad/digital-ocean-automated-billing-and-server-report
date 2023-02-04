import os
import yaml
import traceback
from packages.file import file
from packages.logger import logger
from packages.digitalOcean import digitalOcean


# Initiate logger
log = logger.get(app_name='digital-ocean', enable_logs_file=False)


def main():

    log.info('Start program execution')

    project_abs_path = file.caller_dir_path()

    # Import configurations
    config_path = os.path.join(project_abs_path, 'config.yaml')
    with open(config_path) as config_file:
        config = yaml.safe_load(config_file)

    # Initiate an empty dictionary that will be returned from this program
    output_dict = dict()

    # Create an instance of DigitalOcean
    docn = digitalOcean.DigitalOcean(
        bearer_token=config['digitalOcean']['bearer_token']
    )

    # Get the balance info of the account and add the results dictionary to
    # the output dictionary
    balance_results_dict = docn.get_balance()
    output_dict['balance'] = balance_results_dict

    # Get last invoice
    invoice_results_dict = docn.get_last_invoice()
    output_dict['last_invoice'] = invoice_results_dict

    # Get last payment
    payment_results_dict = docn.get_last_payment()
    output_dict['last_payment'] = payment_results_dict

    # Get droplet specs
    droplet_results_dict = docn.get_droplet_specs(
        droplet_name=config['digitalOcean']['droplet_name']
    )
    output_dict['droplet_specs'] = droplet_results_dict

    # Get CPU metrics for last week
    cpu_results_dict = docn.get_cpu_metrics(
        host_id=config['digitalOcean']['droplet_id'],
        days_count=7
    )
    output_dict['cpu_metrics'] = cpu_results_dict

    # Log the results
    log.info('Month to date usage: {0}'.format(
        output_dict['balance']['month_to_date_usage']
    ))
    log.info('Month to date balance: {0}'.format(
        output_dict['balance']['month_to_date_balance']
    ))
    log.info('Account balance: {0}'.format(
        output_dict['balance']['account_balance']
    ))
    log.info('Last invoice amount: {0}'.format(
        output_dict['last_invoice']['amount']
    ))
    log.info('Last invoice period: {0}'.format(
        output_dict['last_invoice']['invoice_period']
    ))
    log.info('Last payment amount: {0}'.format(
        output_dict['last_payment']['amount']
    ))
    log.info('Last payment date: {0}'.format(
        output_dict['last_payment']['date']
    ))
    log.info('vCPUs: {0}'.format(
        output_dict['droplet_specs']['vcpus']
    ))
    log.info('Memory: {0}'.format(
        output_dict['droplet_specs']['memory']
    ))
    log.info('Disk: {0}'.format(
        output_dict['droplet_specs']['disk']
    ))
    log.info('Monthly price: {0}'.format(
        output_dict['droplet_specs']['price_monthly']
    ))
    log.info('Max CPU: {0}%'.format(
        output_dict['cpu_metrics']['max_cpu_percent']
    ))
    log.info('Max CPU timestamp: {0}'.format(
        output_dict['cpu_metrics']['max_cpu_time']
    ))
    log.info('CPU labels: {0}'.format(
        output_dict['cpu_metrics']['cpu_labels']
    ))
    log.info('CPU data: {0}'.format(
        output_dict['cpu_metrics']['cpu_data']
    ))

    log.info('Finished program execution')

    # Return the output dictionary
    return output_dict


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e)
        log.error('Error Traceback: \n {0}'.format(traceback.format_exc()))
