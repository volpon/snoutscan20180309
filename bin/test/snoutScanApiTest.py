#!/.condaUser/.anaconda3/envs/snoutScan/bin/python3 
import unittest

import requests
import json
import base64

import logging

##################################################

#For testing the cloud instance:
#api_url = 'https://snout-cloud.appspot.com'
#api_verify_ssl=True

#For testing a local instance:
api_url = 'http://127.0.0.1:8080'
api_verify_ssl=False

test_email = "test@a.a"
test_password = "test"

session = requests.Session()
#session.trust_env = False

def do_auth(username, password):
    r = session.post(
        '{0}/api/auth'.format(api_url),
        json={'email': username,'password': password},
        verify=api_verify_ssl)

    if r.status_code != 200:
        return None, None

    res = r.json()

    return res['access_token'], res['profile']

def do_create(self, email, password, fields = None):
    
    json = {'email': email, 'password': password}

    if fields is not None: json.update(fields)
    
    r = session.post('{0}/api/profile/signup'.format(api_url),
        json=json,
        verify=api_verify_ssl)

    if r.status_code == 409:
        return None

    if r.status_code != 201:
        # not created and not exists
        return None

    #print("headers: ", r.headers)

    self.assertEqual(r.status_code, 201)
    res = r.json()

    self.assertTrue(isinstance(res, dict))

    profile_id = res.get('profile_id')
    self.assertTrue(isinstance(profile_id, int))

    return profile_id

def do_delete(self, access_token, profile_id):

    r = session.delete('{0}/api/profile/{1}'.format(api_url, profile_id),
        headers = {'Authorization': 'JWT {0}'.format(access_token) },
        json= {},
        verify=api_verify_ssl)

    self.assertEqual(r.status_code, 204)

def do_add_friend(self, access_token, profile_id, fields = None):
    
        if fields is None:
            fields = {
                'name': 'name1',
                'breed': 'breed1', 
                'sex': 'sex1', 
                'age': 'age1', 
                'location': 'location1',
                'status': 'lost'
            }
    
        r = session.post('{0}/api/profile/{1}/friends/new'.format(api_url, profile_id),
            headers = {'Authorization': 'JWT {0}'.format(access_token) },
            json= fields,
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 201)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        friend_id = res.get('friend_id')
        self.assertTrue(isinstance(friend_id, int))

        return friend_id

def load_image(fname):
    
    with open(fname, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())

    #encoded_image = base64.b64encode(b'0123456789\0AAAA\n\r')
    #print(encoded_image)
    #print("encoded_image size: ", len(encoded_image))

    image_data = str(encoded_image, "utf-8")
    #print(image_data)
    image_type = 'image/jpeg'

    #print("image_data size: ", len(image_data))

    return image_data, image_type

def do_set_photo(self, access_token, friend_id, fname):
    
    image_data, image_type = load_image(fname)
    
    # set photo        
    r = session.put('{0}/api/friend/{1}/photo'.format(api_url, friend_id),
        headers = {'Authorization': 'JWT {0}'.format(access_token) },
        json= {'image': { 'data': image_data, 'type': image_type }},
        verify=api_verify_ssl)

    self.assertEqual(r.status_code, 204)
    return image_data, image_type

##################################################

class Test_signup(unittest.TestCase):

    def test_create_and_delete(self):

        # create profile
        _ = do_create(self, test_email, test_password)

        # login
        access_token, profile_id = do_auth(test_email, test_password)

        # delete profile
        do_delete(self, access_token, profile_id)

    def tearDown(self):
        # login
        access_token, profile_id = do_auth(test_email, test_password)

        # delete profile
        if access_token is not None and profile_id is not None:
            do_delete(self, access_token, profile_id)

class Test_auth(unittest.TestCase):
    
    def setUp(self):
        
        # create profile
        self.profile_id = do_create(self, test_email, test_password)

    def tearDown(self):
        # login
        access_token, profile_id = do_auth(test_email, test_password)

        # delete profile
        if access_token is not None and profile_id is not None:
            do_delete(self, access_token, profile_id)

    def test_1(self):
        access_token, profile_id = do_auth(test_email, test_password)
        self.assertTrue(isinstance(access_token, str))
        self.assertTrue(isinstance(profile_id, int))
        self.assertEqual(profile_id, self.profile_id)

    def test_2(self):
        access_token, _ = do_auth(test_email, test_password+'111')
        self.assertTrue(access_token is None)

    def test_3(self):
        access_token, _ = do_auth('111'+test_email, test_password)
        self.assertTrue(access_token is None)

class Test_profile(unittest.TestCase):
    
    def setUp(self):
        
        # create profile
        _ = do_create(self, test_email, test_password)

        # login
        self.access_token, self.profile_id = do_auth(test_email, test_password)

    def tearDown(self):
        # login
        #access_token, profile_id = do_auth(test_email, test_password)

        # delete profile
        if self.access_token is not None and self.profile_id is not None:
            do_delete(self, self.access_token, self.profile_id)

    def test_get(self):

        r = session.get('{0}/api/profile/{1}'.format(api_url, self.profile_id),
            verify=api_verify_ssl)

        if r.status_code // 100 == 4:
            print("headers: ", r.headers)
            print("text: ", r.text)

        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        self.assertEqual(res.get('profile_id'), self.profile_id)
        self.assertEqual(res.get('email'), None)
        self.assertEqual(res.get('password'), None)
        self.assertTrue(isinstance(res.get('phone'), str))
        self.assertTrue(isinstance(res.get('use_phone'), bool))
        self.assertTrue(isinstance(res.get('use_msg'), bool))

    def test_put_and_get(self):

        # put
        r = session.put('{0}/api/profile/{1}'.format(api_url, self.profile_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json= {
                'phone':'phone1',
                'use_phone': True,
                'use_msg': False,
            },
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 204)

        # get
        r = session.get('{0}/api/profile/{1}'.format(api_url, self.profile_id),
            verify=api_verify_ssl)

        if r.status_code // 100 == 4:
            print("headers: ", r.headers)
            print("text: ", r.text)
        
        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        self.assertEqual(res.get('profile_id'), self.profile_id)
        self.assertEqual(res.get('email'), None)
        self.assertEqual(res.get('password'), None)
        self.assertEqual(res.get('phone'), 'phone1')
        self.assertEqual(res.get('use_phone'), True)
        self.assertEqual(res.get('use_msg'), False)
        
class Test_friends(unittest.TestCase):
    
    def setUp(self):
        
        # create profile
        _ = do_create(self, test_email, test_password)

        # login
        self.access_token, self.profile_id = do_auth(test_email, test_password)

    def tearDown(self):

        # delete profile
        if self.access_token is not None and self.profile_id is not None:
            do_delete(self, self.access_token, self.profile_id)

    def test_get_list(self):

        friend_id2 = do_add_friend(self, self.access_token, self.profile_id, fields = {
                'name': 'name1',
                'breed': 'breed1', 
                'sex': 'sex1', 
                'age': 'age1', 
                'location': 'location1',
                'status': 'lost'
            })

        friend_id2 = do_add_friend(self, self.access_token, self.profile_id, fields = {
                'name': 'name2',
                'breed': 'breed2', 
                'sex': 'sex2', 
                'age': 'age2', 
                'location': 'location2',
                'status': 'lost'
            })

        # get friends list
        r = session.get('{0}/api/profile/{1}/friends'.format(api_url, self.profile_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        friends = r.json()
        self.assertTrue(isinstance(friends, list))

        self.assertEqual(len(friends), 2)

        for friend in friends:
            self.assertTrue(isinstance(friend, dict))
            self.assertTrue(isinstance(friend.get('name'), str))
            self.assertTrue(friend['name'] == 'name1' or friend['name']=='name2')

            sufix = friend['name'][-1]

            self.assertEqual(friend.get('breed'), 'breed'+sufix)
            self.assertEqual(friend.get('sex'), 'sex'+sufix)
            self.assertEqual(friend.get('age'), 'age'+sufix)
            self.assertEqual(friend.get('location'), 'location'+sufix)
            self.assertEqual(friend.get('status'), 'lost')
           
    def test_create_get_delete(self):

        friend_id = do_add_friend(self, self.access_token, self.profile_id, fields = {
                'name': 'name1',
                'breed': 'breed1', 
                'sex': 'sex1', 
                'age': 'age1', 
                'location': 'location1',
                'status': 'lost'
            })

        # get friends list
        r = session.get('{0}/api/profile/{1}/friends'.format(api_url, self.profile_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        friends = r.json()
        self.assertTrue(isinstance(friends, list))
        self.assertEqual(len(friends), 1)
        
        self.assertEqual(friends[0].get('friend_id'), friend_id)
        
        # get friend data
        r = session.get('{0}/api/friend/{1}'.format(api_url, friend_id),
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        friend = r.json()
        self.assertTrue(isinstance(friend, dict))
        
        #self.assertTrue(isinstance(friend.get('name'), str))
        #self.assertTrue(isinstance(friend.get('breed'), str))
        #self.assertTrue(isinstance(friend.get('sex'), str))
        #self.assertTrue(isinstance(friend.get('age'), str))
        #self.assertTrue(isinstance(friend.get('location'), str))

        self.assertEqual(friend.get('friend_id'), friend_id)
        self.assertEqual(friend.get('name'), 'name1')
        self.assertEqual(friend.get('breed'), 'breed1')
        self.assertEqual(friend.get('sex'), 'sex1')
        self.assertEqual(friend.get('age'), 'age1')
        self.assertEqual(friend.get('location'), 'location1')
        self.assertEqual(friend.get('status'), 'lost')

        # delete friend
        r = session.delete('{0}/api/friend/{1}'.format(api_url, friend_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json= {},
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 204)

        # check delete
        # get friends list
        r = session.get('{0}/api/profile/{1}/friends'.format(api_url, self.profile_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        friends = r.json()
        self.assertTrue(isinstance(friends, list))
        self.assertEqual(len(friends), 0)

    def test_put_and_get(self):
    
        friend_id = do_add_friend(self, self.access_token, self.profile_id, fields = {
                'name': 'name1',
                'breed': 'breed1', 
                'sex': 'sex1', 
                'age': 'age1', 
                'location': 'location1',
                'status': 'lost'
            })

        self.assertTrue(isinstance(friend_id,int))

        # put
        r = session.put('{0}/api/friend/{1}'.format(api_url, friend_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json= {
                'name': 'name2',
                'breed': 'breed2', 
                'sex': 'sex2', 
                'age': 'age2', 
                'location': 'location2',
                'status': 'found'
            },
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 204)

        # get
        r = session.get('{0}/api/friend/{1}'.format(api_url, friend_id),
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        friend = r.json()
        self.assertTrue(isinstance(friend, dict))
        
        self.assertEqual(friend.get('friend_id'), friend_id)
        self.assertEqual(friend.get('name'), 'name2')
        self.assertEqual(friend.get('breed'), 'breed2')
        self.assertEqual(friend.get('sex'), 'sex2')
        self.assertEqual(friend.get('age'), 'age2')
        self.assertEqual(friend.get('location'), 'location2')
        self.assertEqual(friend.get('status'), 'found')

class Test_photo(unittest.TestCase):
        
    def setUp(self):
        
        # create profile
        _ = do_create(self, test_email, test_password)

        # login
        self.access_token, self.profile_id = do_auth(test_email, test_password)

        self.friend_id = do_add_friend(self, self.access_token, self.profile_id)

    def tearDown(self):

        # delete profile
        if self.access_token is not None and self.profile_id is not None:
            do_delete(self, self.access_token, self.profile_id)

    def test_put_get(self):
        
        image_data, image_type = do_set_photo(self, self.access_token, self.friend_id, "snout_0003.jpg")

        #print("PUT image_data size: ", len(image_data))

        # get photo        
        r = session.get('{0}/api/friend/{1}/photo'.format(api_url, self.friend_id),
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        image = res.get('image')

        self.assertTrue(isinstance(image, dict))
        self.assertEqual(image.get('data'), image_data)
        self.assertEqual(image.get('type'), image_type)

class Test_match(unittest.TestCase):
    
    def setUp(self):
        
        # create profile
        _ = do_create(self, test_email, test_password)

        # login
        self.access_token, self.profile_id = do_auth(test_email, test_password)

        self.friend_id1 = do_add_friend(self, self.access_token, self.profile_id)
        do_set_photo(self, self.access_token, self.friend_id1, "snout_0001.jpg")

        self.friend_id2 = do_add_friend(self, self.access_token, self.profile_id)
        do_set_photo(self, self.access_token, self.friend_id2, "snout_0002.jpg")

    def tearDown(self):

        # delete profile
        if self.access_token is not None and self.profile_id is not None:
            do_delete(self, self.access_token, self.profile_id)
        pass

    def test_match1(self):

        image_data, image_type = load_image("snout_0001.jpg")

        r = session.post('{0}/api/query_match'.format(api_url),
            json= {'image': { 'data': image_data, 'type': image_type }},
            verify=api_verify_ssl)
        
        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        self.assertEqual(res.get('status'), 'found')
        self.assertEqual(res.get('friend'), self.friend_id1)

    def test_match2(self):
    
        image_data, image_type = load_image("snout_0002.jpg")

        r = session.post('{0}/api/query_match'.format(api_url),
            json= {'image': { 'data': image_data, 'type': image_type }},
            verify=api_verify_ssl)
        
        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        self.assertEqual(res.get('status'), 'found')
        self.assertEqual(res.get('friend'), self.friend_id2)
        
#    def test_matches(self):
#        '''
#        This test tests the api_query_matches endpoint to search for multiple matches.
#        '''
#    
#        image_data, image_type = load_image("snout_0002.jpg")
#
#        r = session.post('{0}/api/query_matches/{1}'.format(api_url, 2),
#            json= {'image': { 'data': image_data, 'type': image_type }},
#            verify=api_verify_ssl)
#        
#        self.assertEqual(r.status_code, 200)
#
#        res = r.json()
#        self.assertTrue(isinstance(res, dict))
#
#        self.assertEqual(res.get('status'), 'found')
#        self.assertEqual(res.get('friend'), self.friend_id2)
       

if __name__ == '__main__':
    print("Testing API_URL: \'{}\'".format(api_url))      

    #logging.basicConfig() 
    #logging.getLogger().setLevel(logging.DEBUG)
    #requests_log = logging.getLogger("requests.packages.urllib3")
    #requests_log.setLevel(logging.DEBUG)
    #requests_log.propagate = True
    
    unittest.main()