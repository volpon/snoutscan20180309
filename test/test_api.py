import unittest

import requests
import json
import base64

##################################################

api_url = 'http://localhost:5555'
api_username = 'a@a.a'
api_password = 'a'
api_verify_ssl=False

test_email = "test@a.a"
test_password = "test"

def do_auth(username, password):
    r = requests.post(
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
    
    r = requests.post('{0}/api/profile/signup'.format(api_url),
        json=json,
        verify=api_verify_ssl)

    if r.status_code == 409:
        return None

    if r.status_code != 201:
        # not created and not exists
        return None

    #self.assertEqual(r.status_code, 201)
    res = r.json()

    self.assertTrue(isinstance(res, dict))

    profile_id = res.get('profile_id')
    self.assertTrue(isinstance(profile_id, int))

    return profile_id

def do_delete(self, access_token, profile_id):

    r = requests.delete('{0}/api/profile/{1}'.format(api_url, profile_id),
        headers = {'Authorization': 'JWT {0}'.format(access_token) },
        json= {},
        verify=api_verify_ssl)

    self.assertEqual(r.status_code, 204)

def do_add_friend(self, access_token, profile_id, fields = None):
    
        r = requests.post('{0}/api/profile/{1}/friends/new'.format(api_url, profile_id),
            headers = {'Authorization': 'JWT {0}'.format(access_token) },
            json= {
                'name': 'name1',
                'breed': 'breed1', 
                'sex': 'sex1', 
                'age': 'age1', 
                'location': 'location1'
            },
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
    r = requests.put('{0}/api/friend/{1}/photo'.format(api_url, friend_id),
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
        access_token, profile_id = do_auth(test_email, test_password)

        # delete profile
        if access_token is not None and profile_id is not None:
            do_delete(self, access_token, profile_id)

    def test_get(self):

        r = requests.get('{0}/api/profile/{1}'.format(api_url, self.profile_id),
            json= {},
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        self.assertEqual(res.get('email'), None)
        self.assertEqual(res.get('password'), None)
        self.assertTrue(isinstance(res.get('phone'), str))

    def test_put_and_get(self):

        # put
        r = requests.put('{0}/api/profile/{1}'.format(api_url, self.profile_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json= {
                'phone':'phone1'
            },
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 204)

        # get
        r = requests.get('{0}/api/profile/{1}'.format(api_url, self.profile_id),
            json= {},
            verify=api_verify_ssl)
        
        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        self.assertEqual(res.get('email'), None)
        self.assertEqual(res.get('password'), None)
        self.assertEqual(res.get('phone'), 'phone1')
        
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

    def test_get(self):

        # get friends list
        r = requests.get('{0}/api/profile/{1}/friends'.format(api_url, self.profile_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        friends = r.json()
        self.assertTrue(isinstance(friends, list))

        for friend in friends:
            self.assertTrue(isinstance(friend, dict))
            self.assertTrue(isinstance(res.get('name'), str))
           
    def test_create_get_delete(self):

        friend_id = do_add_friend(self, self.access_token, self.profile_id, fields = {
                'name': 'name1',
                'breed': 'breed1', 
                'sex': 'sex1', 
                'age': 'age1', 
                'location': 'location1'
            })

        # get friends list
        r = requests.get('{0}/api/profile/{1}/friends'.format(api_url, self.profile_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        friends = r.json()
        self.assertTrue(isinstance(friends, list))
        self.assertEqual(len(friends), 1)
        
        self.assertEqual(friends[0].get('friend_id'), friend_id)
        
        # get friend data
        r = requests.get('{0}/api/friend/{1}'.format(api_url, friend_id),
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        friend = r.json()
        self.assertTrue(isinstance(friend, dict))
        
        self.assertTrue(isinstance(friend.get('name'), str))
        self.assertTrue(isinstance(friend.get('breed'), str))
        self.assertTrue(isinstance(friend.get('sex'), str))
        self.assertTrue(isinstance(friend.get('age'), str))
        self.assertTrue(isinstance(friend.get('location'), str))

        #self.assertEqual(friend.get('name'), 'name1')
        #self.assertEqual(friend.get('breed'), 'breed1')
        #self.assertEqual(friend.get('sex'), 'sex1')
        #self.assertEqual(friend.get('age'), 'age1')
        #self.assertEqual(friend.get('location'), 'location1')

        # delete friend
        r = requests.delete('{0}/api/friend/{1}'.format(api_url, friend_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            json= {},
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 204)

        # check delete
        # get friends list
        r = requests.get('{0}/api/profile/{1}/friends'.format(api_url, self.profile_id),
            headers = {'Authorization': 'JWT {0}'.format(self.access_token) },
            verify=api_verify_ssl)

        self.assertEqual(r.status_code, 200)

        friends = r.json()
        self.assertTrue(isinstance(friends, list))
        self.assertEqual(len(friends), 0)

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
        r = requests.get('{0}/api/friend/{1}/photo'.format(api_url, self.friend_id),
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

        r = requests.post('{0}/api/query_match'.format(api_url),
            json= {'image': { 'data': image_data, 'type': image_type }},
            verify=api_verify_ssl)
        
        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        self.assertEqual(res.get('status'), 'found')
        self.assertEqual(res.get('friend'), self.friend_id1)

    def test_match2(self):
    
        image_data, image_type = load_image("snout_0002.jpg")

        r = requests.post('{0}/api/query_match'.format(api_url),
            json= {'image': { 'data': image_data, 'type': image_type }},
            verify=api_verify_ssl)
        
        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        self.assertEqual(res.get('status'), 'found')
        self.assertEqual(res.get('friend'), self.friend_id2)
       
    def test_match3(self):
        
        image_data, image_type = load_image("snout_0003.jpg")

        r = requests.post('{0}/api/query_match'.format(api_url),
            json= {'image': { 'data': image_data, 'type': image_type }},
            verify=api_verify_ssl)
        
        self.assertEqual(r.status_code, 200)

        res = r.json()
        self.assertTrue(isinstance(res, dict))

        self.assertEqual(res.get('status'), 'not found')

if __name__ == '__main__':
    print("Testing API_URL: \'{}\'".format(api_url))      
    unittest.main()
    #unittest.main(argv=["", "Test_signup"])
    #unittest.main(argv=["", "Test_signup.test_create_and_delete"])
    #unittest.main(argv=["", "Test_auth.test_1"])
    #unittest.main(argv=["", "Test_profile"])
    #unittest.main(argv=["", "Test_friends"])
    #unittest.main(argv=["", "Test_friends.test_create_get_delete"])
    #unittest.main(argv=["", "Test_photo"])
    #unittest.main(argv=["", "Test_photo.test_put_get"])
    #unittest.main(argv=["", "Test_match"])
    #unittest.main(argv=["", "Test_match.test_match1"])
