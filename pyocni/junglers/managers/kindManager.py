class KindManager:
    """

        Manager for Kind documents on couch database

    """

    def get_filtered_kinds(self,jfilters,db_kinds):
        """
        Returns kind documents matching the filter provided
        Args:
            @param jfilters: description of the kind document to retrieve
            @param db_kinds: Kind descriptions that already exist in database
            @return : <list> OCCI kind description contained inside of the kind document
        """
        var = list()
        #Extract kind descriptions from the dictionary
        try:
            for elem in db_kinds:
                for jfilter in jfilters:
                    ok = joker.filter_occi_description(elem,jfilter)
                    if ok is True:
                        var.append(elem)
                        logger.debug("Kind filtered document found")
                        break
            return var,return_code['OK']
        except Exception as e:
            logger.error("filtered kinds : " + e.message)
            return "An error has occurred",return_code['Internal Server Error']


    def register_kinds(self,creator,descriptions,db_occi_ids,db_occi_locs):

        """
        Add new kinds to the database
        Args:
            @param creator: the id of the issuer of the creation request
            @param descriptions: OCCI kind descriptions
            @param db_occi_ids: Kind IDs already existing in the database
            @param db_occi_locs: Kind locations already existing in the database
        """
        loc_res = list()
        resp_code = return_code['OK']
        for desc in descriptions:
            occi_id = joker.get_description_id(desc)
            ok_k = joker.verify_occi_uniqueness(occi_id,db_occi_ids)
            if ok_k is True:
                occi_loc = joker.make_category_location(desc)
                ok_loc = joker.verify_occi_uniqueness(occi_loc,db_occi_locs)
                if ok_loc is True:
                    ok_ar = joker.verify_existences_alpha(desc,db_occi_ids)
                    if ok_ar is True:
                        jData = dict()
                        jData['_id'] = uuid_Generator.get_UUID()
                        jData['Creator'] = creator
                        jData['CreationDate'] = str(datetime.now())
                        jData['LastUpdate'] = ""
                        jData['OCCI_Location']= occi_loc
                        jData['OCCI_Description']= desc
                        jData['OCCI_ID'] = occi_id
                        jData['Type']= "Kind"
                        jData['Provider']= {"local":["dummy"],"remote":[]}
                        loc_res.append(jData)
                    else:
                        message = "Missing action or related kind description, Kind will not be created."
                        logger.error("Register kind : " + message)
                        resp_code = return_code['Not Found']
                        return list(),resp_code

                else:
                    message = "Location conflict, kind will not be created."
                    logger.error("Register kind : " + message)
                    resp_code = return_code['Conflict']
                    return list(),resp_code
            else:
                message = "This kind description already exists in document "
                logger.error("Register kind : " + message)
                resp_code = return_code['Conflict']
                return list(),resp_code

        return loc_res,resp_code


    def update_OCCI_kind_descriptions(self,user_id,new_data,db_data):
        """
        Updates the OCCI description field of the kind which document OCCI_ID is equal to OCCI_ID contained in data
        (Can only be done by the creator of the kind document)
        Args:
            @param user_id: ID of the creator of the kind document
            @param new_data: Data containing the OCCI ID of the kind and the new OCCI kind description
            @param db_data: Categories already contained in the database

        """
        to_update = list()
        resp_code = return_code['OK']
        for desc in new_data:
            occi_id = joker.get_description_id(desc)
            old_doc = joker.extract_doc(occi_id,db_data)
            if old_doc is not None:
                if user_id == old_doc['Creator']:
                    problems,occi_description= joker.update_occi_category_description(old_doc['OCCI_Description'],desc)
                    if problems is True:
                        message = "Kind OCCI description " + occi_id + " has not been totally updated."
                        logger.error("Kind OCCI description update " + message)
                        return list(),return_code['Bad Request']
                    else:
                        message = "Kind OCCI description " + occi_id + " has been updated successfully"
                        old_doc['OCCI_Description'] = occi_description
                        old_doc['LastUpdate'] = str(datetime.now())
                        to_update.append(old_doc)
                        logger.debug("Update kind OCCI description : " + message)
                else:
                    message = "You have no right to update this kind document " + occi_id
                    logger.error("Update kind OCCI des : " + message)
                    return list(),return_code['Forbidden']
            else:
                message = "Kind document " + occi_id + " couldn\'t be found "
                logger.error("Update kind OCCI des : " + message)
                return list(),return_code['Not Found']
        return to_update,resp_code

    def update_kind_providers(self,user_id,new_data,db_data):
        """
        Updates the provider field of the kind which document OCCI_ID is equal to OCCI_ID contained in data
        (Can only be done by the creator of the kind document)
        Args:
            @param user_id: ID of the creator of the kind document
            @param new_data: Data containing the OCCI ID of the kind and the new kind provider description
            @param db_data: Categories already contained in the database

        """
        to_update = list()
        resp_code = return_code['OK']
        for desc in new_data:
            occi_id = desc['OCCI_ID']
            old_doc = joker.extract_doc(occi_id,db_data)
            if old_doc is not None:
                if user_id == old_doc['Creator']:
                    provider_description,problems= doc_Joker.update_kind_provider(old_doc['Provider'],desc['Provider'])
                    if problems is True:
                        message = "Kind provider description " + occi_id + " has not been totally updated."
                        logger.error("Kind provider description update " + message)
                        return list(),return_code['Bad Request']
                    else:
                        message = "Kind provider description " + occi_id + " has been updated successfully"
                        old_doc['Provider'] = provider_description
                        old_doc['LastUpdate'] = str(datetime.now())
                        to_update.append(old_doc)
                        logger.debug("Update kind provider description : " + message)
                else:
                    message = "You have no right to update this kind document " + occi_id
                    logger.error("Update kind provider des : " + message)
                    return list(),return_code['Forbidden']
            else:
                message = "Kind document " + occi_id + " couldn\'t be found "
                logger.error("Update kind provider des : " + message)
                return list(),return_code['Not Found']
        return to_update,resp_code


    def delete_kind_documents(self,descriptions,user_id,db_categories,db_entities):
        """
        Delete kind documents that is related to the scheme + term contained in the description provided
        Args:
            @param descriptions: OCCI description of the kind document to delete
            @param user_id: id of the issuer of the delete request
            @param db_categories: Category data already contained in the database
            @param db_entities: Entity data already contained in the database
        """

        message = list()
        res_code = return_code['OK']
        #Verify the existence of such kind document
        for desc in descriptions:
            occi_id = joker.get_description_id(desc)
            kind_id_rev = joker.verify_exist_occi_id_creator(occi_id,user_id,db_categories)
            if kind_id_rev is not None:
                exist_entities = self.get_entities_belonging_to_kind(occi_id,db_entities)
                if exist_entities is False:
                    message.append(kind_id_rev)
                    event = "Kind document " + occi_id + " is sent for delete "
                    logger.debug("Delete kind : " + event)
                else:
                    event = "Unable to delete because this kind document " + occi_id + " has resources depending on it. "
                    logger.error("Delete kind : " + event)
                    return list(), return_code['Bad Request']
            else:
                event = "Could not find this kind document " + occi_id +" or you are not authorized for for delete"
                logger.error("Delete kind : " + event)
                return list(), return_code['Bad Request']
        return message,res_code

    def get_entities_belonging_to_kind(self, occi_id,db_data):
        """
        Verifies if there are entities of this kind
        Args:
            @param occi_id: OCCI_ID of the kind
            @param db_data: OCCI_IDs of the kind that has entities running
        """
        try:
            db_data.index(occi_id)
        except ValueError as e:
            logger.debug("Entities belong kind : " + e.message)
            return False
        return True