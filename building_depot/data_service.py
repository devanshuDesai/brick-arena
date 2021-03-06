'''
data_service.py
~~~~~~


@copyright: (c) 2013 SynergyLabs
@license:   UCSD License. See License file for details.
'''
import json
from .bd_service import BuildingDepotService


class DataService(BuildingDepotService):

    def __init__(self, base_url, api_key, username=None, auth_token=None,
                 expiration=None, verify=False):
        super(DataService, self).__init__('%s' % base_url,
                                          username=username,
                                          api_key=api_key,
                                          auth_token=auth_token,
                                          expiration=expiration,
                                          verify=verify)

    @property
    def api_url(self):
        if self.auth_token is None:
            return '%s/admin/api' % self.base_url
        return '%s/api' % self.base_url

    def get_paging_params(self, offset, limit):
        params = {
            'offset': offset,
            'limit': limit,
        }
        return params

    def index(self):
        '''
        Retrieve some public information about the Data Service including its
        available subresources.
        using api : GET /
        return the original response as dict
        '''
        r = self.get(self.api_url)
        response = r.json()
        return response

    def info(self):
        '''
        Retrieve more detailed information about the Data Service including the
        location of a buildings.xml file that describes the buildings belonging
        to this DataService.
        using api : GET /info
        return the original response as dict
        '''
        r = self.get('%s/info' % self.api_url, auth=self._auth)
        response = r.json()
        return response

    def add_admin_sensornetworks(self, username, sensor_networks):
        '''Adds (associates) SensorNetworks to the specified Admin.'''
        url = '%s/admins/%s/sensornetworks' % (self.api_url, username)
        data = {
            'sensor_networks': sensor_networks,
        }
        self.post(url, auth=self._auth, headers=self._init_headers,
                  json_data=data)

    def get_subscribers(self):
        '''
        Retreives a list of Subscribers. Must have appropriate access_level to
        successfully make this request.
        using api: GET /subscribers
        '''
        # TODO need new doc
        r = self.get('%s/subscribers' % self.api_url, auth=self._auth,
                     headers=self._init_headers)
        return r.json()

    def create_subscribers(self, **data):
        '''
        Create a new Subscriber.
        using api: POST /subscribers
        kwarg data format:
        data = {
            'username': username,
        }
        '''
        r = self.post('%s/subscribers' % self.api_url, auth=self._auth,
                      json_data=data, headers=self._init_headers)
        return r.json()['uri']

    def view_subscribers(self, email):
        '''
        Retreive information about the Subscriber account associated with
        username.
        using api: GET /subscribers/<user email>
        '''
        r = self.get('%s/subscribers/%s' % (self.api_url, email),
                     auth=self._auth, headers=self._init_headers)
        return r.json()

    def delete_subscribers(self, email):
        '''
        Delete the Subscriber associated with particular username.
        using api: DELETE /subscribers/<user email>
        '''
        self.delete('%s/subscribers/%s' % (self.api_url, email),
                    auth=self._auth, headers=self._init_headers)

    def list_subscribers(self):
        '''
        Retreives a list of Subscribers. Must have appropriate access_level to
        successfully make this request.
        using api: GET /subscribers
        '''
        r = self.get('%s/subscribers' % self.api_url,
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def list_subscriber_sensors(self, email):
        '''
        Retreive a list of Sensors subscribed to by a specific Subscriber
        using api: GET /subscribers/<user_email>/sensors
        '''
        r = self.get('%s/subscribers/%s/sensors' % (self.api_url, email),
                     auth=self._auth, headers=self._init_headers)
        return r.json()

    def list_subscriber_changes(self, email):
        '''
        Retreive a list of all changed Sensorpoints for Sensors subscribed to
        by specific Subscriber
        using api: GET /subscribers/<user_email>/changes
        '''
        r = self.get('%s/subscribers/%s/changes' % (self.api_url, email),
                     auth=self._auth, headers=self._init_headers)
        return r.json()

    def clear_subscriber_changes(self, email):
        '''
        Clear list of all changed Sensorpoints for Sensors subscribed to by
        specific Subscriber
        using api: DELETE /subscribers/<user_email>/changes
        '''
        r = self.delete('%s/subscribers/%s/changes' % (self.api_url, email),
                        auth=self._auth, headers=self._init_headers)
        return r

    def list_sensors(self, query_context=None, offset=0, limit=1000):
        '''
        Retreive a list of Sensors accessible to the User initiating the
        request. This list can be context filtered by specifying the context
        query string.
        using api: GET /sensors
        '''
        params = self.get_paging_params(offset, limit)
        if query_context is not None:
            params['context'] = json.dumps(query_context)
        r = self.get('%s/sensors' % self.api_url, auth=self._auth,
                     headers=self._init_headers, params=params)
        return r.json()

    def create_sensor(self, **data):
        '''
        Creates a Sensor.
        using api: POST /sensors
        kwarg data format
        data = {
            'source_name': source_name,
            'source_identifier': source_id,
            'template': template,
            'network': network,
            'context': context,
        }
        '''
        r = self.post('%s/sensors' % self.api_url, auth=self._auth,
                      headers=self._init_headers, json_data=data)
        uri = r.json()['uri']
        uuid = uri.split('/')[-1]
        return uuid

    def view_sensor(self, uuid):
        '''
        Retreive information about the Sensor associated with the UUID
        sensor_uuid.
        using api: GET /sensors/<sensor_uuid>
        '''
        r = self.get('%s/sensors/%s' % (self.api_url, uuid), auth=self._auth,
                     headers=self._init_headers)
        return r.json()

    def update_sensor(self, uuid, **data):
        '''
        Updates the Sensor associated with sensor_uuid.
        using api: POST /sensors/<sensor_uuid>
        kwarg data format
        data = {
            'source_name': source_name,
            'source_identifier': source_id,
        }
        '''
        self.post('%s/sensors/%s' % (self.api_url, uuid), auth=self._auth,
                  headers=self._init_headers, json_data=data)

    def delete_sensor(self, uuid):
        '''
        Delete the Sensor associated with sensor_uuid.
        using api: DELETE /sensors/<sensor_uuid>
        '''
        self.delete('%s/sensors/%s' % (self.api_url, uuid), auth=self._auth,
                    headers=self._init_headers)

    def list_sensor_subscribers(self, uuid):
        '''
        Retreive the list of Subscribers for this sensor
        using api: GET /sensors/<sensor_uuid>/subscribers
        '''
        r = self.get('%s/sensors/%s/subscribers' % (self.api_url, uuid),
                     auth=self._auth, headers=self._init_headers)
        return r.json()

    def subscriber_sensor(self, uuid, **data):
        '''
        Subscribe to the Sensor referenced by sensor_uuid
        using api: POST /sensors/<sensor_uuid>/subscribers
        kwarg data format
        data = {
            'username': username,
            'user_email': email,
        }
        '''
        self.post('%s/sensors/%s/subscribers' % (self.api_url, uuid),
                  auth=self._auth, headers=self._init_headers, json_data=data)

    def unsubscriber_sensor(self, uuid, email):
        '''
        Unsubscribe from the Sensor associated with sensor_uuid.
        using api: DELETE /sensors/<sensor_uuid>/subscribers/<email>
        '''
        url = '%s/sensors/%s/subscribers/%s' % (self.api_url, uuid, email)
        self.delete(url, auth=self._auth, headers=self._init_headers)

    def list_sensorpoints(self, uuid, offset=0, limit=1000):
        '''
        This retreives a list of Sensorpoints for the Sensor associated with
        sensor_uuid.
        using api: GET /sensors/<sensor_uuid>/sensorpoints
        '''
        params = self.get_paging_params(offset, limit)
        r = self.get('%s/sensors/%s/sensorpoints' % (self.api_url, uuid),
                     headers=self._init_headers, auth=self._auth,
                     params=params)
        return r.json()

    def create_sensorpoint(self, uuid, **data):
        '''
        Creates a Sensorpoint for a specific Sensor.
        using api: POST /sensors/<sensor_uuid>/sensorpoints
        kwarg data format
        data = {
          type (string) - SensorpointType name (See List SensorpointTypes)
          update_period (int) - Periodicity of Sensorpoint updates (in seconds)
          max_val (int) - Maximum value for the Sensorpoint data
          min_val (int) - Minimum value for the Sensorpoint data
          readonly (bool) - Read/Writeable status
          active (bool) - Status of the Sensorpoint
        }
        '''
        default_data = {
            'max_val': 0,
            'min_val': 0,
            'update_period': 0,
            'readonly': False,
            'active': True,
        }
        default_data.update(data)
        r = self.post('%s/sensors/%s/sensorpoints' % (self.api_url, uuid),
                      headers=self._init_headers, auth=self._auth,
                      json_data=default_data)
        return r.json()['uri']

    def view_sensorpoint(self, uuid, tp):
        '''
        Retrieves information about a Sensorpoint.
        using api: GET /sensors/<sensor_uuid>/sensorpoints/<type>
        '''
        url = '%s/sensors/%s/sensorpoints/%s' % (self.api_url, uuid, tp)
        r = self.get(url, headers=self._init_headers, auth=self._auth)
        return r.json()

    def update_sensorpoint(self, uuid, tp, **data):
        '''
        Updates the Sensorpoint of type associated with sensor_uuid.
        using api: POST /sensors/<sensor_uuid>/sensorpoints/<type>
        kwarg data format:
        data = {
          update_period (int) - Periodicity of Sensorpoint updates (in seconds)
          max_val (int) - Maximum value for the Sensorpoint data
          min_val (int) - Minimum value for the Sensorpoint data
          readonly (bool) - Read/Writeable status
          active (bool) - Status of the Sensorpoint
        }
        '''
        self.post('%s/sensors/%s/sensorpoints/%s' % (self.api_url, uuid, tp),
                  headers=self._init_headers, auth=self._auth, json_data=data)

    def delete_sensorpoint(self, uuid, tp):
        '''
        Delete the Sensorpoint of type associated with sensor_uuid. Note that
        only Sensorpoints that are not specified in the parent Sensor's
        SensorTemplate can be deleted i.e Sensorpoints that have from_template
        set to false.
        using api: DELETE /sensors/<sensor_uuid>/sensorpoints/<type>
        '''
        self.delete('%s/sensors/%s/sensorpoints/%s' % (self.api_url, uuid, tp),
                    headers=self._init_headers, auth=self._auth)

    def get_timeseries_datapoints(self, uuid, tp, start, stop):
        '''
        This retreives a list of datapoints for the timeseries of the specified
        Sensorpoint for the specified time interval start to stop
        using api: GET /sensors/<sensor_uuid>/sensorpoints/<type>/timeseries
        with query param 'start' and 'end'
        '''
        start = start if type(start) is str else start.isoformat()
        stop = stop if type(stop) is str else stop.isoformat()
        params = {
            'start': start,
            'stop': stop,
        }
        url = '%s/sensors/%s/sensorpoints/%s/timeseries' \
              % (self.api_url, uuid, tp)
        r = self.get(url, headers=self._init_headers, auth=self._auth,
                     params=params)
        return r.json()

    def get_latest_timeseries_datapoint(self, uuid, tp):
        '''
        This retreives the last (latests) datapoint for the timeseries of the
        specified Sensorpoint. See Get Timeseries Datapoints to retrieve
        timeseries dataoints for a specific timespan
        using api: GET /sensors/<sensor_uuid>/sensorpoints/<type>/timeseries
        '''
        url = '%s/sensors/%s/sensorpoints/%s/timeseries' % \
              (self.api_url, uuid, tp)
        r = self.get(url, headers=self._init_headers, auth=self._auth)
        return r.json()

    def get_timeseries_datapoints_batch(self, batch_query, timeout=15):
        '''This retreives a timeseries for a batch of Sensorpoints. The time
        interval of each timeseries can be specified using the start and stop
        parameters or left as null to retrieve the latest datapoint. The format
        for all timestamps is the ISO datetime format
        YYYY-MM-DDTHH:MM:SS.ssssss and all timestamps are in the UTC timezone.

        batch_query is a dictionary:
            key is sensor uuid, value is a dictionry:
                the key is spname, and the value is start and end dict
        '''
        data = {
            'batch': batch_query,
        }
        url = '%s/batch/timeseries/retrieve' % self.api_url
        r = self.post(url, headers=self._init_headers, auth=self._auth,
                      json_data=data, timeout=timeout)
        return r.json()['batch']

    def put_timeseries_datapoints(self, uuid, tp, datapoints):
        '''
        This stores datapoints in the timeseries of the specified Sensorpoint.
        using api: POST /sensors/<sensor_uuid>/sensorpoints/<type>/timeseries
        '''
        url = '%s/sensors/%s/sensorpoints/%s/timeseries' \
              % (self.api_url, uuid, tp)
        data = {
            'datapoints': datapoints,
        }
        r = self.post(url, headers=self._init_headers, auth=self._auth,
                      json_data=data)
        return r.json()

    def put_timeseries_datapoints_batch(self, **batch_data):
        '''
        This posts specified datapoints to the timeseries for a batch of
        Sensorpoints. Batch must always be a dictionary of sensors which
        in turn should contain a dictionary of SensorPoints and associated
        timeseries datapoints to post.
        '''
        data = {
            'batch': batch_data,
        }
        url = '%s/batch/timeseries/create' % self.api_url
        r = self.post(url, headers=self._init_headers, auth=self._auth,
                      json_data=data)
        return r.json()

    def list_sensor_context(self, uuid, offset=0, limit=1000):
        '''
        Retreive a list of Contexts for a specific sensor.
        using api: GET /sensors/(sensor_uuid)/contexts
        '''
        params = self.get_paging_params(offset, limit)
        r = self.get('%s/sensors/%s/contexts' % (self.api_url, uuid),
                     headers=self._init_headers, auth=self._auth,
                     params=params)
        return r.json()

    def add_sensor_context(self, uuid, **data):
        '''
        Adds (associates) a Context to the specified Sensor.
        using api: POST /sensors/(sensor_uuid)/contexts
        kwarg data format:
        data = {
            keyword (string) - Valid Keyword name (See List Keyword)
            tag (string) - Context tag
        }
        '''
        r = self.post('%s/sensors/%s/contexts' % (self.api_url, uuid),
                      headers=self._init_headers, auth=self._auth,
                      json_data=data)
        return r.json()

    def remove_sensor_context(self, uuid, cid):
        '''
        Removes (disassociates) the specified Context from the Sensor.
        using api: DELETE /sensors/(sensor_uuid)/contexts
        '''
        self.delete('%s/sensors/%s/contexts/%s' % (self.api_url, uuid, cid),
                    headers=self._init_headers, auth=self._auth)

    def list_sensorpoint_type(self, offset=0, limit=1000):
        '''
        This retreives a list of all SensorpointTypes.
        using api: GET /sensorpointtypes
        '''
        params = self.get_paging_params(offset, limit)
        r = self.get('%s/sensorpointtypes' % self.api_url, params=params,
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def create_sensorpoint_type(self, **data):
        '''
        Creates a new SensorpointType.
        using api: POST /sensorpointtypes
        kwarg data format:
        data = {
            name (string) - Unique SensorpointType name
            description (string) - Description of SensorpointType
            data_type (string) - Data Type for the SensorpointType (See Data
            Types)
            timeseries_type (string) - optional Timeseries type for the
            SensorpointType. Either 'conti- nous' or 'discrete'. Defaults to
            'continuos'.
            unit (string) - optional SensorpointType unit (Long form)
            shorthand_unit (string) - optional SensopointType unit (Short form)
        }
        '''
        r = self.post('%s/sensorpointtypes' % self.api_url,
                      headers=self._init_headers, auth=self._auth,
                      json_data=data)
        return r.json()['uri']

    def view_sensorpoint_type(self, name):
        '''
        This retreives information about the SensorpointType associated with
        name.
        using api: GET /sensorpointtypes/(name)
        '''
        r = self.get('%s/sensorpointtypes/%s' % (self.api_url, name),
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def delete_sensorpoint_type(self, name):
        '''
        This deletes the SensorpointType associated with name. Note that only
        user created SensorpointTypes may be deleted
        using api: DELETE /sensorpointtypes/(name)
        '''
        self.delete('%s/sensorpointtypes/%s' % (self.api_url, name),
                    headers=self._init_headers, auth=self._auth)

    def list_sensor_templates(self, offset=0, limit=1000):
        '''
        This retreives a list of all SensorTemplates.
        using api: GET /sensortemplates
        '''
        params = self.get_paging_params(offset, limit)
        r = self.get('%s/sensortemplates' % self.api_url, params=params,
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def create_sensor_template(self, **data):
        '''
        Creates a new SensorTemplate.
        using api: POST /sensortemplates
        kwarg data format:
        data = {
            name (string) - Unique SensorTemplate name
            description (string) - Description of SensorTemplate
            sensorpoint_types (list) - List of names of SensorPointTypes that
            should be part of the template (See List SensorPointTypes)
        }
        '''
        r = self.post('%s/sensortemplates' % self.api_url,
                      headers=self._init_headers, auth=self._auth,
                      json_data=data)
        return r.json()['uri']

    def view_sensor_template(self, name):
        '''
        This retreives information about the SensorTemplate associated with
        name.
        using api: GET /sensortemplates/(name)
        '''
        r = self.get('%s/sensortemplates/%s' % (self.api_url, name),
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def delete_sensor_template(self, name):
        '''
        This deletes the SensorTemplate associated with name. Note that only
        user created SensorTemplates may be deleted
        using api: DELETE /sensortemplates/(name)
        '''
        self.delete('%s/sensortemplates/%s' % (self.api_url, name),
                    headers=self._init_headers, auth=self._auth)

    def add_sensor_template_sensorpoint_type(self, name, sp_type_name):
        '''
        Adds (associates) a SensorpointType to the specified SensorTemplate.
        using api: POST /sensortemplates/(name)/sensorpointtypes
        '''
        data = {
            'sensorpoint_type': sp_type_name
        }
        r = self.post('%s/sensortemplates/%s/sensorpointtypes' %
                      (self.api_url, name), json_data=data,
                      headers=self._init_headers, auth=self._auth)
        return r.json()['uri']

    def remove_sensor_template_sensorpoint_type(self, name, sp_type_name):
        '''
        Removes (disassociates) the specified SensorpointType from the
        SensorTemplate.
        using api: DELETE /sensortemplates/(name)/sensorpointtypes/
        (sp_type_name)
        '''
        self.delete('%s/sensortemplates/%s/sensorpointtypes/%s' %
                    (self.api_url, name, sp_type_name),
                    headers=self._init_headers, auth=self._auth)

    def list_sensor_groups(self, offset=0, limit=1000):
        '''
        This retreives a list of all SensorGroups.
        using api: GET /sensorgroups
        '''
        params = self.get_paging_params(offset, limit)
        r = self.get('%s/sensorgroups' % self.api_url, params=params,
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def create_sensor_group(self, **data):
        '''
        Creates a new SensorGroup for specified name.
        using api: POST /sensorgroups
        kwargs data format:
        data = {
            name (string) - Unique SensorGroup name
            definition (dictionary) - Context information that
              defines the Sensors in this Group. (See List Sensors By Context)
            auto (boolean) - Automanage Sensorgroup Flag
        }
        '''
        r = self.post('%s/sensorgroups' % self.api_url, json_data=data,
                      headers=self._init_headers, auth=self._auth)
        return r.json()['uri']

    def view_sensor_group(self, name):
        '''
        This retreives information about the SensorGroup associated with name.
        using api: GET /sensorgroups/(name)
        '''
        r = self.get('%s/sensorgroups/%s' % (self.api_url, name),
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def delete_sensor_group(self, name):
        '''
        This deletes the SensorGroup associated with name.
        using api: DELETE /sensorgroups/(name)
        '''
        self.delete('%s/sensorgroups/%s' % (self.api_url, name),
                    headers=self._init_headers, auth=self._auth)

    def list_sensor_group_sensors(self, name, context, offset=0, limit=1000):
        '''
        Retreive the list of Sensors belonging to the Sensorgroup. This list
        can be context filtered by specifying the context query string.
        using api: GET /sensorgroups/(name)/sensors
        '''
        params = self.get_paging_params(offset, limit)
        params['context'] = json.dumps(context)
        r = self.get('%s/sensorgroups/%s/sensors' % (self.api_url, name),
                     params=params, headers=self._init_headers,
                     auth=self._auth)
        return r.json()

    def list_permissions(self, entity=None, offset=0, limit=1000):
        '''
        entity: email address
        This retreives a list of all Permissions. The list of permissions can
        also be filtered by entity by appending a query string such as
        ?entity="user@host.com" to the base url. ex.
        /permissions?entity="user@host.com"
        using api: GET /permissions
        '''
        params = self.get_paging_params(offset, limit)
        if entity is not None:
            params['entity'] = entity
        r = self.get('%s/permissions' % self.api_url, params=params,
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def create_permission(self, **data):
        '''
        Creates a new permission for specified entity.
        using api: POST /permissions
        kwarg data format:
        data = {
            entity (string) - Entity to grant permission. Could be
                              a user email or domain name
            read (bool) - Read permission assigned (true/false)
            write (bool) - Write permission assigned (true/false)
            sensorgroup (string) - Name of SensorGroup to assign permissions to
            sensor (string) - UUID of Sensor to assign permissions to
        }
        '''
        r = self.post('%s/permissions' % self.api_url, json_data=data,
                      headers=self._init_headers, auth=self._auth)
        return r.json()['uri']

    def view_permission(self, pid):
        '''
        This retreives information about the Permission associated with id.
        using api: GET /permissions/(id)
        '''
        r = self.get('%s/permissions/%d' % (self.api_url, pid),
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def delete_permission(self, pid):
        '''
        This deletes the permissions associated with id.
        using api: DELETE /permissions/(id)
        '''
        self.delete('%s/permissions/%d' % (self.api_url, pid),
                    headers=self._init_headers, auth=self._auth)

    def list_keywords(self, offset=0, limit=1000):
        '''
        Retreive a list of all available Keywords.
        using api: GET /keywords
        '''
        params = self.get_paging_params(offset, limit)
        r = self.get('%s/keywords' % self.api_url, params=params,
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def create_keyword(self, **data):
        '''
        Creates a Keyword.
        using api: POST /keywords
        kwarg data format:
        data = {
            name (string) - Unique Keyword name (identifier)
            descrition (string) - Description of the Keyword
        }
        '''
        r = self.post('%s/keywords' % self.api_url, json_data=data,
                      headers=self._init_headers, auth=self._auth)
        return r.json()['uri']

    def view_keyword(self, name):
        '''
        View the information of a keyword
        using api: GET /keywords/(name)
        '''
        r = self.get('%s/keywords/%s' % (self.api_url, name),
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def update_keyword(self, name, **data):
        '''
        Updates the Keyword associated with name identifier.
        using api: POST /keywords/(name)
        kwarg data format:
        data = {
            name (string) - Unique Keyword name (identifier)
            descrition (string) - Description of the Keyword
        }
        '''
        self.post('%s/keywords/%s' % (self.api_url, name), json_data=data,
                  headers=self._init_headers, auth=self._auth)

    def delete_keyword(self, name):
        '''
        Delete the Keyword associated with name identifier.
        using api: DELETE /keywords/(name)
        '''
        self.delete('%s/keywords/%s' % (self.api_url, name),
                    headers=self._init_headers, auth=self._auth)

    def list_contexts(self, offset=0, limit=1000):
        '''
        Retreive a list of all available Contexts.
        using api: GET /contexts
        '''
        params = self.get_paging_params(offset, limit)
        r = self.get('%s/contexts' % self.api_url, params=params,
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def create_context(self, **data):
        '''
        Creates a Context.
        using api: POST /contexts
        kwarg data format:
        data = {
            keyword (string) - Valid Keyword name (See List Keywords)
            tag (string) - Context tag
        }
        '''
        r = self.post('%s/contexts' % self.api_url, json_data=data,
                      headers=self._init_headers, auth=self._auth)
        return r.json()['uri']

    def view_context(self, cid):
        '''
        The Context associated with the identifier id.
        using api: GET /contexts/(cid)
        '''
        r = self.get('%s/contexts/%s' % (self.api_url, cid),
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def update_context(self, cid, **data):
        '''
        Updates the Context specified by id identifier.
        using api: POST /contexts/(cid)
        data = {
            keyword (string) - Valid Keyword name (See List Keywords)
            tag (string) - Context tag
        }
        '''
        self.post('%s/contexts/%s' % (self.api_url, cid), json_data=data,
                  headers=self._init_headers, auth=self._auth)

    def delete_context(self, cid):
        '''
        Delete the Context specified by id identifier.
        using api: DELETE /contexts/(id)
        '''
        self.delete('%s/contexts/%s' % (self.api_url, cid),
                    headers=self._init_headers, auth=self._auth)

    def top_level_location_tier(self):
        '''
        Retreives the top level location tier for this DataService which can be
        used to traverse the Location structure of the
        Sensors for this DataService
        using api: GET /locations
        '''
        r = self.get('%s/locations' % self.api_url,
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def get_location_list_by_tier(self, tier_hierarchy, offset=0, limit=1000):
        '''
        This retreives a list of User accounts. Must be Admin to send this
        request.
        using api: GET /locations/(path: tier_hierarchy)
        '''
        params = self.get_paging_params(offset, limit)
        r = self.get('%s/locations/%s' % (self.api_url, tier_hierarchy),
                     headers=self._init_headers, auth=self._auth,
                     params=params)
        return r.json()

    def view_location(self, tier_hierarchy, name):
        '''
        This retreives information about the Location associated with
        location_name.
        using api: GET /locations/(path: tier_hierarchy)/(name)
        '''
        url = '%s/locations/%s/%s' % (self.api_url, tier_hierarchy, name)
        r = self.get(url, headers=self._init_headers, auth=self._auth)
        return r.json()

    def update_location(self, tier_hierarchy, name, **data):
        '''
        Updates a Location item. Currently only the description of a location
        can be updated.
        using api:  POST /locations/(path: tier_hierarchy)/(name)
        kwarg data format:
        data = {
            description (string) - Description for Location associated with
            location_name
        }
        '''
        self.post('%s/locations/%s/%s' % (self.api_url, tier_hierarchy, name),
                  headers=self._init_headers, auth=self._auth, json_data=data)

    def get_sensor_networks(self, offset=0, limit=1000):
        '''
        Retreive a list of all available SensorNetworks.
        using api: GET /sensornetworks
        '''
        params = self.get_paging_params(offset, limit)
        r = self.get('%s/sensornetworks' % self.api_url, params=params,
                     headers=self._init_headers, auth=self._auth)
        return r.json()

    def create_sensor_network(self, **data):
        '''
        Creates a SensorNetwork.
        Restricted to Admins only.
        using api: POST /sensornetworks
        kwarg data format:
        data = {
            name (string) - Unique SensorNetwork name (identifier)
            description (string) - Description of the SensorNetwork
        }
        '''
        r = self.post('%s/sensornetworks' % self.api_url, json_data=data,
                      headers=self._init_headers, auth=self._auth)
        return r.json()['uri']

    def view_sensor_network(self, network_name):
        '''
        Name: Unique identifier associated with the sensor network.
        using api: GET /sensornetworks/(network_name)
        '''
        r = self.get('%s/sensornetworks/%s' % (self.api_url, network_name),
                     headers=self._init_headers, auth=self._auth)
        return r.json()
