#!python

import configparser, json, os, shutil, subprocess, time, obspython as obs

### GLOBALS / DEFAULTS
props = None
settings = obs.obs_data_create_from_json_file_safe(os.path.join(os.path.dirname(__file__), 'config', 'browser_source_default.json'), 'backup')

def obslog(lvl, msg):
    obs.blog(lvl, "BROWSER_SOURCE_SCRIPT: " + msg)

### UTILITY FUNCTIONS ###
def populate_browser_source_file(user_config_path):
    if user_config_path == None:
        obslog(obs.LOG_INFO, "Deploying as configured")
        global settings
        if not obs.obs_data_save_json_safe(settings, os.path.join(os.path.dirname(__file__), 'config', 'browser_source.json'), 'tmp', 'backup'):
            obslog(obs.LOG_ERROR, "unable to create config save")
    else:
        obslog(obs.LOG_INFO, "Deploying with saved configuration")
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'config', 'browser_source.json'), os.path.join(os.path.dirname(__file__), 'config', 'browser_source.json.backup'))
        shutil.copyfile(user_config_path, os.path.join(os.path.dirname(__file__), 'config', 'browser_source.json'))
    
### IMAGE HELPERS
def image_exists(image):
    return image in subprocess.run("docker images --format \"{{.Repository }}:{{.Tag }}\"", \
            stdout=subprocess.PIPE, universal_newlines=True).stdout

def build_browser_source_image():
    build = subprocess.run('docker build --rm \"' + os.path.dirname(__file__) + '\" -t browsersource:latest', \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return build.stdout, build.stderr

def remove_image(image):
    remove = subprocess.run('docker rmi -f ' + image, \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return remove.stdout, remove.stderr

### CONTAINER HELPERS
def container_exists(container):
    return container in subprocess.run('docker ps -a --format \"{{.Names}}\"', \
        stdout=subprocess.PIPE, universal_newlines=True).stdout

def start_browser_source_container():
    run = subprocess.run('docker run -d --name browser-source -p 5000:5000 browsersource:latest', \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return run.stdout, run.stderr

def remove_container(container):
    subprocess.run('docker stop -f ' + container)
    remove = subprocess.run('docker rm -f ' + container, \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return remove.stdout, remove.stderr


### BUTTON HANDLERS
def deploy_browser_source_server(prop, props):
    remove_browser_source_server(None, None)
    obslog(obs.LOG_INFO, "deploy_browser_source_server")

    isUserConfig = obs.obs_data_get_bool(settings, 'use_user_config')
    userConfigPath = obs.obs_data_get_string(settings, 'user_config')
    if isUserConfig:
        if not userConfigPath:
            obslog(obs.LOG_WARNING, "Cannot deploy, no user config path specified")
            raise Exception("Unable to deploy container, selected use saved config but not path specified")
        try:
            with open(userConfigPath, errors = 'replace') as f:
                json.load(f)
        except json.JSONDecodeError:
            obslog(obs.LOG_ERROR, "Invalid JSON: " + userConfigPath)
            raise
        except OSError:
            obslog(obs.LOG_ERROR, "Unable to open " + userConfigPath)
            raise
        populate_browser_source_file(userConfigPath)
    else:
        populate_browser_source_file(None)

    if image_exists('browsersource:latest'):
        obslog(obs.LOG_INFO, "browser-source image found")
        obslog(obs.LOG_INFO, "launching browser-source container")
        run = start_browser_source_container()
        obslog(obs.LOG_INFO, "rnstdout: " + run[0] + "; runstderr: " +run[1])
    else:
        build = build_browser_source_image()
        obslog(obs.LOG_INFO, "buildstdout: " + build[0] + "; buildstderr: " + build[1])
        
        wait_limit = 10
        while True:
            if image_exists('browsersource:latest'):
                obslog(obs.LOG_INFO, "browser-source image built")
                obslog(obs.LOG_INFO, "launching browser-source container")
                run = start_browser_source_container()
                obslog(obs.LOG_INFO, "runstdout: " + run[0] + "; runstderr: " + run[1])
                break
            else:
                obslog(obs.LOG_INFO, "browser-source image not found")
                time.sleep(2)
                wait_limit -= 1
                if wait_limit == 0:
                    obslog(obs.LOG_ERROR, "unable to start browser-source container")
    #TODO create browser source, if desired
    obslog(obs.LOG_INFO,"exiting deploy_browser_source_server")

def remove_browser_source_server(prop, props):
    obslog(obs.LOG_INFO, "remove_browser_source_server")
    if container_exists('browser-source'):
        obslog(obs.LOG_INFO, "removing containers")
        remove = remove_container('browser-source')
        obslog(obs.LOG_INFO, "remove_container stdout: " + remove[0] + "; removestderr: " + remove[1])
    if image_exists('browsersource:latest'):
        obslog(obs.LOG_INFO, "removing image")
        remove = remove_image('browsersource:latest')
        obslog(obs.LOG_INFO, "remove_image stdout: " + remove[0] + "; removestderr: " + remove[1])
    obslog(obs.LOG_INFO, "exiting remove_browser_source_server")


def is_user_config(props, prop, data):
    if data:
        config = obs.obs_data_get_json(data)
        configjson = json.loads(str(config))
        del(config)

        isUserConfig = 'use_user_config' in configjson.keys() and configjson['use_user_config']
        if isUserConfig:
            global settings
            settings = configjson
        else:
            for a_prop in ('score_names', 'font', 'fgcolor', 'bgcolor'):
                thisprop = obs.obs_properties_get(props, a_prop)
                obs.obs_property_set_visible(thisprop, not isUserConfig)
                del(thisprop)
            config_path_property = obs.obs_properties_get(props, 'user_config')
            obs.obs_property_set_visible(config_path_property, isUserConfig)

            del(config_path_property)

    return True

### OBSPYTHON SCRIPT FUNCTIONS
def script_properties():
    global props
    props = obs.obs_properties_create()
    checkbox = obs.obs_properties_add_bool(props, "use_user_config", "Use Saved Config")
    obs.obs_property_set_modified_callback(checkbox, is_user_config)
    del(checkbox)
    obs.obs_properties_add_path(props, "user_config", "Saved Config Path", obs.OBS_PATH_FILE, "*.json", os.path.join(os.path.dirname(__file__), 'config'))
    obs.obs_properties_add_editable_list(props, "score_names", "Scores To Track", obs.OBS_EDITABLE_LIST_TYPE_STRINGS, "", "")
    obs.obs_properties_add_font(props, "font", "Scores Font")
    obs.obs_properties_add_color(props, "fgcolor", "Text Color")
    obs.obs_properties_add_color(props, "bgcolor", "Background Color")
    obs.obs_properties_add_button(props, "deploy", "Deploy Browser Source Server", deploy_browser_source_server)
    obs.obs_properties_add_button(props, "remove", "Remove Browser Source Server", remove_browser_source_server)
    obslog(obs.LOG_INFO, "properties loaded")

    #TODO checkbox to add to create browser source
    #TODO browser source name
    return props

def script_unload():
    obslog(obs.LOG_INFO, "script_unload")
    remove_browser_source_server(None, None)

def script_load(_):
    obslog(obs.LOG_INFO, "script_onload")
