from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, SiteItem, PaginationItem
import logging
import copy

logger = logging.getLogger('tableau.endpoint.sites')


class Sites(Endpoint):
    def __init__(self, parent_srv):
        super(Endpoint, self).__init__()
        self.parent_srv = parent_srv

    @property
    def baseurl(self):
        return "{0}/sites".format(self.parent_srv.baseurl)

    # Gets all sites
    def get(self, req_options=None):
        logger.info('Querying all sites on site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content)
        all_site_items = SiteItem.from_response(server_response.content)
        return all_site_items, pagination_item

    # Gets 1 site by id
    def get_by_id(self, site_id):
        if not site_id:
            error = "Site ID undefined."
            raise ValueError(error)
        logger.info('Querying single site (ID: {0})'.format(site_id))
        url = "{0}/{1}".format(self.baseurl, site_id)
        server_response = self.get_request(url)
        return SiteItem.from_response(server_response.content)[0]

    # Update site
    def update(self, site_item):
        if not site_item.id:
            error = "Site item missing ID."
            raise MissingRequiredFieldError(error)
        if site_item.admin_mode:
            if site_item.admin_mode == SiteItem.AdminMode.ContentOnly and site_item.user_quota:
                error = 'You cannot set admin_mode to ContentOnly and also set a user quota'
                raise ValueError(error)

        url = "{0}/{1}".format(self.baseurl, site_item.id)
        update_req = RequestFactory.Site.update_req(site_item)
        server_response = self.put_request(url, update_req)
        logger.info('Updated site item (ID: {0})'.format(site_item.id))
        update_site = copy.copy(site_item)
        return update_site._parse_common_tags(server_response.content)

    # Delete 1 site object
    def delete(self, site_id):
        if not site_id:
            error = "Site ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, site_id)
        self.delete_request(url)
        logger.info('Deleted single site (ID: {0})'.format(site_id))

    # Create new site
    def create(self, site_item):
        if site_item.admin_mode:
            if site_item.admin_mode == SiteItem.AdminMode.ContentOnly and site_item.user_quota:
                error = 'You cannot set admin_mode to ContentOnly and also set a user quota'
                raise ValueError(error)

        url = self.baseurl
        create_req = RequestFactory.Site.create_req(site_item)
        server_response = self.post_request(url, create_req)
        new_site = SiteItem.from_response(server_response.content)[0]
        logger.info('Created new site (ID: {0})'.format(new_site.id))
        return new_site
