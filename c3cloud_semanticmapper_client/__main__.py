from os.path import join, dirname

from c3cloud_semanticmapper_client import client
import sys
import argparse
from c3cloud_semanticmapper_client.lib import *
from c3cloud_semanticmapper_client.c3_cloud_excel_loader import *
from c3cloud_semanticmapper_client import c3_cloud_excel_loader


def parseargs():
    args = sys.argv
    parser = argparse.ArgumentParser(description='load an xlsx file to the terminology mapper')
    parser.add_argument('--interactive', '-i', help='should the program be interactive', action='store_true')
    parser.add_argument('--dry-run', '-d', help='read-only mode, do not perform any change', action='store_true')
    parser.add_argument('--force', '-f', help='in case of conflicts, force overwrite with the local data (by default only adds new mappings)', action='store_true')
    parser.add_argument('--NUKE', help='reset of the database before running. erases everything and starts with the fresh file', action='store_true')
    parser.add_argument('--url', '-u', help='url to which the requests should be sent. default "https://rubis.limics.upmc.fr/c3-cloud/"', default="https://rubis.limics.upmc.fr/c3-cloud/")
    parser.add_argument('--config', '-c', help='path to the config file to use.', required = True)
    parser.add_argument('--verbose', '-v', help='verbose output', action='store_true')
    ## parser.add_argument('--apikey-path', '-k', help='path to the api key file', required = True)

    cliargs = parser.parse_args()
    print(cliargs)
    return cliargs

def main(cliargs):    
    global codesystems, baseurl

    c3_cloud_excel_loader.illegals = set()

    
    
    def run():
        root_path = os.path.dirname(cliargs.config)
        def fullpath(e):
            return os.path.join(root_path, e)
    
        config = load_config(cliargs.config)
        config['root_path'] = root_path
        print(config)
    
        
        client.__init__(cliargs, config)
        
        
        printinfo('Using "{}" as base url'.format(client.baseurl))
    
        if cliargs.NUKE:
            printwarn('!!!!!!!! !!! deleting everything !!! !!!!!!!!')
            input()
            ans = client.sendrequest('all', method='delete')
            print(ans)
            
        fetch_data_form_server()
        if 'terminologies' in config.keys():
            upload_terminologies(fullpath(config['terminologies']))
        if 'verbosity' in config.keys():
            client.verbosity = ['info','warning','error'].index(config['verbosity'])
        l = [importFile(fullpath(k), e['sheets'])
            for k, e in config['mappings'].items()]
        #print(l)
        #uploadItems(l)
        
    run()
        
    print('done.')
    print('──────────────────────────────')
    print('Discarded designations:', c3_cloud_excel_loader.illegals)
    for category, count in client.report.items():
        print('{}: {}'.format(category, count))


if __name__ == "__main__":
    print(sys.argv)
    cliargs = parseargs()
    main(cliargs)
