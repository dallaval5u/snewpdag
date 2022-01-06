#from . import app
#import snewpdag

import hop, sys, time, os, json, click
sys.path.insert(1, '/home/riccardo/Documents/GitHub/snewpdag')
from snewpdag import dag
#help(dag)
import snewpdag.dag.app
from hop import stream
from . import snews_pt_utils
from hop.io import StartPosition



def save_message(message, counter):
    """ Save messages to a json file.

    """
    
    S = Subscriber()
    path = f'SNEWS_MSGs/'
    os.makedirs(path, exist_ok=True)
    file = path + 'subscribed_messages.json'
    # read the existing file
    try:
        data = json.load(open(file))
        if not isinstance(data, dict):
            print('Incompatible file format!')
            return None
        # TODO: deal with `list` type objects
    except:
        data = {}
    # add new message with a current time stamp
    current_time = S.snews_time()
    #RICCARDO: temporarily add name of injecting node and type of action
    index_coincidence = str(counter)
    #data['coinc' + index_coincidence] = message
    data['action'] = 'alert'
    data['burst_id'] = 0
    data['name'] = 'Control'
    data['coinc_id'] = 1
    data['number_of_coinc_dets'] = index_coincidence
    data['coinc' + index_coincidence] = message
    
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

def display(message):
    """ Function to format output messages
    """
    click.echo(click.style('ALERT MESSAGE'.center(65, '_'), bg='red', bold=True))
    for k, v in message.items():
        if type(v) == type(None): v = 'None'
        if type(v) == int:
            click.echo(f'{k:<20s}:{v:<45}')
        if type(v) == str:
            click.echo(f'{k:<20s}:{v:<45}')
        elif type(v) == list:
            items = '\t'.join(v)
            if k == 'detector_names':
                click.echo(f'{k:<20s}' + click.style(f':{items:<45}', bg='blue'))
            else:
                click.echo(f'{k:<20s}:{items:<45}')
    click.secho('_'.center(65, '_'), bg='bright_red')

class Subscriber:
    """ Class to subscribe ALERT message stream

    Parameters
    ----------
    env_path : `str`
        path for the environment file.
        Use default settings if not given

    """
    def __init__(self, env_path=None):
        snews_pt_utils.set_env(env_path)
        #self.obs_broker = os.getenv("OBSERVATION_TOPIC")
        self.alert_topic = "kafka://localhost:9092/snews.alert-test"
        self.times = snews_pt_utils.TimeStuff()

        # time object/strings
        self.times = snews_pt_utils.TimeStuff(env_path)
        self.hr = self.times.get_hour()
        self.date = self.times.get_date()
        self.snews_time = lambda: self.times.get_snews_time()
        

    def subscribe(self):
        ''' Subscribe and listen to a given topic

        Parameters
        ----------
            Whether to display the subscribed message content

        '''
#        click.echo('You are subscribing to ' +
#                   click.style(f'ALERT', bg='red', bold=True) + '\nBroker:' +
#                   click.style(f'{ self.alert_topic}', bg='green'))

        # Initiate hop_stream
#        print(json.dumps(
#                                               { 'action': 'al\
#ert',\
#                                                                                       'burst_id': \
#                                                 0, 'trial_id': 0, 'name':'Control' })\
#                     )
       # stream = Stream(start_at=StartPosition.EARLIEST)
        
        #stream = Stream()
        try:
            #print('ok')
#            with stream.open(self.alert_topic, "r") as s:
            counter = 0
            s=stream.open(self.alert_topic,\
                           "r")

            for message in s:
                     counter += 1
                     save_message(message, counter)
                     

                     print('this is a test to see if I can print a \
edited message for when an alert is received')
                     #snewpdag.dag.app.run()
                     #print(json.dumps(
        #        { 'action': 'alert', 'burst_id': 0, 'trial_id': 0, 'name':'Control' }))

                     #s.close()
                    # print('ok')
                     #print(sys.stdin)
                     print('this is my mesaage')
                     print(message)
                     if counter > 1:
                          snewpdag.dag.app.run()
 
                     #print('ok')
                     
                    # dag.run()
 #                   s.close()
#                    print(json.dumps(message))
                    #s.close()
#                    app.run()
                    #trial2:
                    #python snewpdag/trials/Simple.py Control -n 1 #| \
                        #          #python -m snewpdag --log INFO --jsonlines snewpdag/data/test-liq-config.py
                    #snews_pt_utils.display_gif()
                    #1display(message)
        except KeyboardInterrupt:
            click.secho('Done', fg='green')
