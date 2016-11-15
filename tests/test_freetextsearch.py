import json
import unittest

from tests import GenericTestCase


class FreeTextSearchTestCase(GenericTestCase):


    def _assert_search_result(self,
                            json_response,
                            name = None,
                            full_name = None,
                            description = None,
                            min_association_number =0):
        self.assertTrue(json_response['data'])
        first_result = json_response['data'][0]['data']
        self.assertEqual(first_result['name'], name)
        if full_name is not None:
            self.assertEqual(first_result['full_name'], full_name)
        if description is not None:
            self.assertEqual(first_result['description'], description)
        self.assertGreaterEqual(first_result['association_counts']['total'], min_association_number)

    #@unittest.skip("testBraf")
    def testBraf(self):

        response= self._make_request('/api/latest/public/search',
                                     data={'q':'braf'},
                                     token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self._assert_search_result(json_response,
                                   'BRAF',
                                   'B-Raf proto-oncogene, serine/threonine kinase',
                                   'Protein kinase involved in the transduction of mitogenic signals from the cell membrane to the nucleus. May play a role in the postsynaptic responses of hippocampal neuron. Phosphorylates MAP2K1, and thereby contributes to the MAP kinase signal transduction pathway.',
                                   680)
        
    #@unittest.skip("testSearchFields")
    def testSearchFields(self):

        response= self._make_request('/api/latest/public/search',
                                     data={'q':'braf', 'fields':['id', 'approved_symbol'], 'size':1},
                                     token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(json_response['data']), 1)
        self.assertEqual(json_response['data'][0]['highlight'], '')
        self.assertEqual(json_response['data'][0]['id'], 'ENSG00000157764')
        
        first_result = json_response['data'][0]['data']
        self.assertEqual(len(first_result), 2)
        self.assertEqual(first_result['approved_symbol'], 'BRAF')
        self.assertEqual(first_result['id'], 'ENSG00000157764')

    # @unittest.skip("testSearchFieldsWithHighlight")
    def testSearchFieldsWithHighlight(self):

        response = self._make_request('/api/latest/public/search',
                                      data={'q': 'braf',
                                            'fields': ['id', 'approved_symbol'],
                                            'highlight': True},
                                      token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['data'][0]['highlight'] is not '')
        highlight = json_response['data'][0]['highlight']

        self.assertGreater(len(highlight), 1)

        self.assertEqual(json_response['data'][0]['id'], 'ENSG00000157764')

        first_result = json_response['data'][0]['data']
        self.assertEqual(len(first_result), 2)
        self.assertEqual(first_result['approved_symbol'], 'BRAF')
        self.assertEqual(first_result['id'], 'ENSG00000157764')

    def testSearchNoHighlight(self):
        response = self._make_request('/api/latest/public/search',
                                      data={'q': 'braf',
                                            'highlight': False},
                                      token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertNotIn('highlight',json_response['data'][0])


    #@unittest.skip("testBestHitSearchFieldsNoFilter")
    def testBestHitSearchFieldsNoFilter(self):
        response= self._make_request('/api/latest/private/besthitsearch',
                                    data={'q':['braf', 'nr3c1', 'Rpl18a', 'rippa', 'ENSG00000157764', 'eff']},                                  
                                    token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(len(json_response['data']), 6)
         
        braf_data = json_response['data'][0]
        self.assertEqual( braf_data['highlight'], '')
        self.assertEqual( braf_data['id'], 'ENSG00000157764')
        self.assertEqual(braf_data['q'], 'braf')
 
        first_result_braf =braf_data['data']
        self.assertNotEqual(len(first_result_braf), 2) #should have more fields since we are not restricting
        self.assertEqual(first_result_braf['approved_symbol'], 'BRAF')
        self.assertEqual(first_result_braf['id'], 'ENSG00000157764')
         
        nr3c1_data = json_response['data'][1]
        self.assertEqual( nr3c1_data['highlight'], '')
        self.assertEqual( nr3c1_data['id'], 'ENSG00000113580')
         
        first_result_nr3c1 =nr3c1_data['data']
        self.assertNotEqual(len(first_result_nr3c1), 2)
        self.assertEqual(first_result_nr3c1['approved_symbol'], 'NR3C1')
        self.assertEqual(first_result_nr3c1['id'], 'ENSG00000113580')
         
        #test fuzzy result
        fuzzy_result = json_response['data'][2]
        self.assertEqual(fuzzy_result['q'], 'Rpl18a')
        fuzzy_result_data = fuzzy_result['data']
        self.assertNotEqual(fuzzy_result_data['approved_symbol'], 'RPL18A')
 
        #test empty result
        empty_result = json_response['data'][3]
        self.assertEqual(empty_result['q'], 'rippa')
        self.assertEqual(empty_result['id'], None)
         
        #test  when query is ENS ID
        ens_data = json_response['data'][4]
        self.assertEqual( ens_data['highlight'], '')
        self.assertEqual( ens_data['id'], 'ENSG00000157764')
        self.assertEqual(ens_data['q'], 'ENSG00000157764')
 
        first_result_ens =ens_data['data']
        self.assertNotEqual(len(first_result_ens), 2)
        self.assertEqual(first_result_ens['approved_symbol'], 'BRAF')
        self.assertEqual(first_result_ens['id'], 'ENSG00000157764')
        
        #test eff which can be desease or target depending on how search is done
        eff_data = json_response['data'][5]
        self.assertGreaterEqual(len(eff_data['data']),1) #no restrictions on returned fields
        self.assertEqual(eff_data['q'], 'eff')
        self.assertEqual(eff_data['exact'], False)


    #@unittest.skip(" testBestHitSearchFieldsTarget")
    def testBestHitSearchFieldsTarget(self):
        response= self._make_request('/api/latest/private/besthitsearch',
                                    data={'q':['braf', 'nr3c1', 'Rpl18a', 'rippa', 'ENSG00000157764', 'eff'],
                                           'filter':'target'},
                                    token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(len(json_response['data']),6)
        
        braf_data = json_response['data'][0]
        self.assertEqual( braf_data['highlight'], '')
        self.assertEqual( braf_data['id'], 'ENSG00000157764')
        self.assertEqual( braf_data['q'], 'braf')
        self.assertEqual( braf_data['exact'], True)

        first_result_braf =braf_data['data']
        self.assertEqual(len(first_result_braf), 1)
        self.assertEqual(first_result_braf['approved_symbol'], 'BRAF')

        nr3c1_data = json_response['data'][1]
        self.assertEqual( nr3c1_data['highlight'], '')
        self.assertEqual( nr3c1_data['id'], 'ENSG00000113580')
        self.assertEqual( nr3c1_data['exact'], True)
        
        first_result_nr3c1 =nr3c1_data['data']
        self.assertEqual(len(first_result_nr3c1), 1)
        self.assertEqual(first_result_nr3c1['approved_symbol'], 'NR3C1')

        #test fuzzy result
        fuzzy_result = json_response['data'][2]
        self.assertEqual(fuzzy_result['q'], 'Rpl18a')
        fuzzy_result_data = fuzzy_result['data']
        self.assertNotEqual(fuzzy_result_data['approved_symbol'], 'RPL18A')

        #test empty result
        empty_result = json_response['data'][3]
        self.assertEqual(empty_result['q'], 'rippa')
        self.assertEqual(empty_result['id'], None)
        
        #test  when query is ENS ID
        ens_data = json_response['data'][4]
        self.assertEqual( ens_data['highlight'], '')
        self.assertEqual( ens_data['id'], 'ENSG00000157764')
        self.assertEqual( ens_data['q'], 'ENSG00000157764')
        self.assertEqual( ens_data['exact'], True)

        first_result_ens =ens_data['data']
        self.assertEqual(len(first_result_ens), 1)
        self.assertEqual(first_result_ens['approved_symbol'], 'BRAF')

        eff_data = json_response['data'][5]
        self.assertEqual(eff_data['q'], 'eff')
        self.assertEqual(eff_data['exact'], False)
        self.assertEqual(len(eff_data['data']),1) #should only get name and id
        self.assertEqual(eff_data['data']['approved_symbol'],'UBE2D3')
          
    
        
    #@unittest.skip(" testBestHitSearchFieldsDisease")
    def testBestHitSearchFieldsDisease(self):
        response= self._make_request('/api/latest/private/besthitsearch',
                                    data={'q':['braf', 'nr3c1', 'Rpl18a', 'rippa', 'ENSG00000157764', 'eff'], 'filter':'disease'},
                                    token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(len(json_response['data']), 6)
        
        braf_data = json_response['data'][0]#should get nothing for target when searching for diseases
        self.assertEqual( braf_data['id'], None)
        self.assertEqual(braf_data['q'], 'braf')

        nr3c1_data = json_response['data'][1]
        self.assertEqual(nr3c1_data['q'], 'nr3c1')
        self.assertEqual( nr3c1_data['id'], None)
        
        #test fuzzy result
        fuzzy_result = json_response['data'][2]
        self.assertEqual(fuzzy_result['q'], 'Rpl18a')
        self.assertEqual( fuzzy_result['id'], None)

        #test empty result
        empty_result = json_response['data'][3]
        self.assertEqual(empty_result['q'], 'rippa') #good there is not a disease with my name! -)
        self.assertEqual(empty_result['id'], None)
        
        #test  when query is ENS ID
        ens_data = json_response['data'][4]
        self.assertEqual( ens_data['id'], None)
        self.assertEqual( ens_data['q'], 'ENSG00000157764')
        
        #test eff which can be desease or target depending on how search is done
        eff_data = json_response['data'][5]
        self.assertEqual(eff_data['q'], 'eff')
        self.assertEqual(eff_data['exact'], False)
        self.assertEqual(len(eff_data['data']),1) #should only get name and id
        self.assertEqual(eff_data['data']['name'],'insulin resistance')
        
    
    ##@unittest.skip("testBestHitSearchFieldsPostTarget")    
    def testBestHitSearchFieldsPostTarget(self):
        
        #passing some dummy fields 'fields':['field1', 'field2'] just to show 
        #that they are going to be overwritten and data will have only two
        # fields: approved_symbol and id
        response= self._make_request('/api/latest/private/besthitsearch',
                                     data=json.dumps({
                                            'q':['braf', 'nr3c1', 'Rpl18a', 'rippa', 'ENSG00000157764', 'eff'], 
                                            'fields':['field1', 'field2'], 
                                            'filter':'target'}),
                                     content_type='application/json',
                                     method='POST',
                                     token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(len(json_response['data']), 6)
        
        braf_data = json_response['data'][0]
        self.assertEqual( braf_data['highlight'], '')
        self.assertEqual( braf_data['id'], 'ENSG00000157764')
        self.assertEqual( braf_data['exact'], True)
        
        first_result_braf =braf_data['data']
        self.assertEqual(len(first_result_braf), 1)
        self.assertEqual(first_result_braf['approved_symbol'], 'BRAF')
        
        
        nr3c1_data = json_response['data'][1]
        self.assertEqual( nr3c1_data['highlight'], '')
        self.assertEqual( nr3c1_data['id'], 'ENSG00000113580')
        self.assertEqual( nr3c1_data['exact'], True)

        first_result_nr3c1 =nr3c1_data['data']
        self.assertEqual(len(first_result_nr3c1), 1)
        self.assertEqual(first_result_nr3c1['approved_symbol'], 'NR3C1')
        
        
        #test fuzzy result
        fuzzy_result = json_response['data'][2]
        self.assertEqual(fuzzy_result['q'], 'Rpl18a')
        self.assertEqual(fuzzy_result['exact'], False)

        fuzzy_result_data = fuzzy_result['data']
        self.assertNotEqual(fuzzy_result_data['approved_symbol'], 'RPL18A')


        #test empty result
        empty_result = json_response['data'][3]
        self.assertEqual(empty_result['q'], 'rippa')
        self.assertEqual(empty_result['id'], None)
        
        #test  when query is ENS ID
        ens_data = json_response['data'][4]
        self.assertEqual( ens_data['highlight'], '')
        self.assertEqual( ens_data['id'], 'ENSG00000157764')
        self.assertEqual( ens_data['q'], 'ENSG00000157764')
        self.assertEqual( ens_data['exact'], True)
        
        first_result_ens =ens_data['data']
        self.assertEqual(len(first_result_ens), 1)
        self.assertEqual(first_result_ens['approved_symbol'], 'BRAF')
    
        
        eff_data = json_response['data'][5]
        self.assertEqual(eff_data['q'], 'eff')
        self.assertEqual(eff_data['exact'], False)
        self.assertEqual(len(eff_data['data']),1) #should only get name and id
        self.assertEqual(eff_data['data']['approved_symbol'],'UBE2D3')
        
    #@unittest.skip("testAsthma")
    def testAsthma(self):
        response= self._make_request('/api/latest/public/search',
                                     data={'q':'asthma'},
                                     token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self._assert_search_result(json_response,
                                   'asthma',
                                   'asthma',
                                   "A bronchial disease that is characterized by chronic inflammation and narrowing of the airways, which is caused by a combination of environmental and genetic factors resulting in recurring periods of wheezing (a whistling sound while breathing), chest tightness, shortness of breath, mucus production and coughing. The symptoms appear due to a variety of triggers such as allergens, irritants, respiratory infections, weather changes, excercise, stress, reflux disease, medications, foods and emotional anxiety.",
                                   2086)


    def _assert_quicksearch_result(self,
                            json_response,
                            name = None,
                            full_name = None,
                            description = None,
                            min_association_number =0):
        self.assertTrue(json_response['data'])
        self.assertIsNotNone(json_response['data']['besthit'])
        first_result = json_response['data']['besthit']['data']
        self.assertEqual(first_result['name'], name)
        if full_name is not None:
            self.assertEqual(first_result['full_name'], full_name)
        if description is not None:
            self.assertEqual(first_result['description'], description)
        self.assertGreaterEqual(first_result['association_counts']['total'], min_association_number)

    #@unittest.skip("testQuickSearchBraf")
    def testQuickSearchBraf(self):
        response= self._make_request('/api/latest/private/quicksearch',
                                     data={'q':'braf'},
                                     token=self._AUTO_GET_TOKEN)
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self._assert_quicksearch_result(json_response,
                                   'BRAF',
                                   'B-Raf proto-oncogene, serine/threonine kinase',
                                   'Protein kinase involved in the transduction of mitogenic signals from the cell'
                                   ' membrane to the nucleus. May play a role in the postsynaptic responses of '
                                   'hippocampal neuron. Phosphorylates MAP2K1, and thereby contributes to the MAP '
                                   'kinase signal transduction pathway.',
                                   680)

    #@unittest.skip("testQuickSearchBrafOrtholog")
    def testQuickSearchBrafOrtholog(self):
        '''lin-45 is a braf ortholog in c.elegans'''
        response= self._make_request('/api/latest/private/quicksearch',
                                     data={'q':'lin-45'},
                                     token=self._AUTO_GET_TOKEN)
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self._assert_quicksearch_result(json_response,
                                   'BRAF',
                                   'B-Raf proto-oncogene, serine/threonine kinase',
                                   'Protein kinase involved in the transduction of mitogenic signals from the cell'
                                   ' membrane to the nucleus. May play a role in the postsynaptic responses of '
                                   'hippocampal neuron. Phosphorylates MAP2K1, and thereby contributes to the MAP '
                                   'kinase signal transduction pathway.',
                                   680)

    #@unittest.skip("testQuickSearchBrafOrtholog_misp")
    def testQuickSearchBrafOrtholog_misp(self):
        '''lin-45 is a braf ortholog in c.elegans, but 50% percent of people willuse lin45
        '''
        response= self._make_request('/api/latest/private/quicksearch',
                                     data={'q':'lin-45'},
                                     token=self._AUTO_GET_TOKEN)
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self._assert_quicksearch_result(json_response,
                                   'BRAF',
                                   'B-Raf proto-oncogene, serine/threonine kinase',
                                   'Protein kinase involved in the transduction of mitogenic signals from the cell'
                                   ' membrane to the nucleus. May play a role in the postsynaptic responses of '
                                   'hippocampal neuron. Phosphorylates MAP2K1, and thereby contributes to the MAP '
                                   'kinase signal transduction pathway.',
                                   680)
        
        
    #@unittest.skip("testQuickSearchAsthma")
    def testQuickSearchAsthma(self):

        response= self._make_request('/api/latest/private/quicksearch',
                                     data={'q':'asthma'},
                                     token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self._assert_quicksearch_result(json_response,
                                   'asthma',
                                   'asthma',
                                   "A bronchial disease that is characterized by chronic inflammation and narrowing of "
                                   "the airways, which is caused by a combination of environmental and genetic factors "
                                   "resulting in recurring periods of wheezing (a whistling sound while breathing), "
                                   "chest tightness, shortness of breath, mucus production and coughing. The symptoms "
                                   "appear due to a variety of triggers such as allergens, irritants, respiratory "
                                   "infections, weather changes, excercise, stress, reflux disease, medications, "
                                   "foods and emotional anxiety.",
                                   2086)

    #@unittest.skip("testQuickSearchCancer")
    def testQuickSearchCancer(self):

        response = self._make_request('/api/latest/private/quicksearch',
                                      data={'q': 'cancer'},
                                      token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self._assert_quicksearch_result(json_response,
                                        'cancer',
                                        'cancer',
                                        "A malignant neoplasm in which new abnormal tissue grow by excessive cellular "
                                        "division and proliferation more rapidly than normal and continues to grow "
                                        "after the stimuli that initiated the new growth cease.",
                                        20000)
    
    @unittest.skip("testAutocomplete")
    def testAutocomplete(self):
        response= self._make_request('/api/latest/private/autocomplete',
                                     data={'q':'ast'},
                                     token=self._AUTO_GET_TOKEN)

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        print json_response




if __name__ == "__main__":
     unittest.main()
