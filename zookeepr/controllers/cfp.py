import sys

from formencode import validators
from formencode.schema import Schema
from formencode.variabledecode import NestedVariables

from zookeepr.lib.auth import *
from zookeepr.lib.base import *
from zookeepr.lib.mail import *
from zookeepr.lib.validators import BaseSchema, ProposalTypeValidator, FileUploadValidator, AssistanceTypeValidator, EmailAddress, NotExistingPersonValidator
from zookeepr.model import ProposalType, Proposal, Attachment, AssistanceType

from zookeepr.config.lca_info import lca_info

class NewPersonSchema(BaseSchema):
    email_address = EmailAddress(resolve_domain=True, not_empty=True)
    firstname = validators.String(not_empty=True)
    lastname = validators.String(not_empty=True)
    address1 = validators.String(not_empty=True)
    address2 = validators.String()
    city = validators.String(not_empty=True)
    state = validators.String()
    postcode = validators.String(not_empty=True)
    country = validators.String(not_empty=True)
    company = validators.String()
    phone = validators.String()
    mobile = validators.String()
    password = validators.String(not_empty=True)
    password_confirm = validators.String(not_empty=True)
    experience = validators.String()
    bio = validators.String(not_empty=True)
    url = validators.String()

    pre_validators = [NotExistingPersonValidator()]
    chained_validators = [validators.FieldsMatch('password', 'password_confirm')]

class ExistingPersonSchema(BaseSchema):
    experience = validators.String()
    bio = validators.String(not_empty=True)
    url = validators.String()
    mobile = validators.String(not_empty=True)

class ProposalSchema(BaseSchema):
    title = validators.String(not_empty=True)
    abstract = validators.String(not_empty=True)
    type = ProposalTypeValidator()
    assistance = AssistanceTypeValidator()
    project = validators.String()
    url = validators.String()
    abstract_video_url = validators.String()

class ExistingCFPSchema(BaseSchema):
    person = ExistingPersonSchema()
    proposal = ProposalSchema()
    #attachment = FileUploadValidator()
    pre_validators = [NestedVariables]

class NewNewCFPSchema(BaseSchema):
    person = NewPersonSchema()
    proposal = ProposalSchema()
    #attachment = FileUploadValidator()
    pre_validators = [NestedVariables]

class NewMiniPersonSchema(BaseSchema):
    email_address = EmailAddress(resolve_domain=True, not_empty=True)
    password = validators.String(not_empty=True)
    password_confirm = validators.String(not_empty=True)
    firstname = validators.String(not_empty=True)
    lastname = validators.String(not_empty=True)
    handle = validators.String(not_empty=True)

    experience = validators.String()
    bio = validators.String(not_empty=True)
    url = validators.String()
    
    pre_validators = [NotExistingPersonValidator()]
    chained_validators = [validators.FieldsMatch('password', 'password_confirm')]

class ExistingMiniPersonSchema(BaseSchema):
    experience = validators.String()
    bio = validators.String(not_empty=True)
    url = validators.String()

class MiniProposalSchema(BaseSchema):
    title = validators.String(not_empty=True)
    abstract = validators.String(not_empty=True)
    type = ProposalTypeValidator()
    assistance = AssistanceTypeValidator()
    #project = validators.String(not_empty=True)
    url = validators.String()
    #abstract_video_url = validators.String()

class NewNewMiniSchema(BaseSchema):
    person = NewMiniPersonSchema()
    proposal = MiniProposalSchema()
    attachment = FileUploadValidator()
    pre_validators = [NestedVariables]

class ExistingMiniSchema(BaseSchema):
    person = ExistingMiniPersonSchema()
    proposal = MiniProposalSchema()
    attachment = FileUploadValidator()
    pre_validators = [NestedVariables]


class CfpController(SecureController):
    #permissions removed since submit* displays appropirate template file upon closed/not_open settings.
    permissions = {
      'index': True,
      'submit': True,
      'submit_mini': True,
    }

    def __init__(self, *args):
        c.cfp_status = lca_info['cfp_status']
        c.cfmini_status = lca_info['cfmini_status']


        # When the CFP status is closed or not open we allow anonymous requests to the submit() action which responds appropriately with a nice message. 
        #if c.cfp_status == 'closed' or c.cfp_status == 'not_open':
        #    self.permissions['submit'] = True
        #if c.cfmini_status == 'closed' or c.cfmini_status == 'not_open':
        #    self.permissions['submit_mini'] = True

    def index(self):
        return render_response("cfp/list.myt")

    def submit(self):
        # if call for papers has closed:
        if c.cfp_status == 'closed':
           return render_response("cfp/closed.myt")
        elif c.cfp_status == 'not_open':
           return render_response("cfp/not_open.myt")
        else:
            c.cfptypes = self.dbsession.query(ProposalType).all()
            c.tatypes = self.dbsession.query(AssistanceType).all()

            errors = {}
            defaults = dict(request.POST)

            if request.method == 'POST' and defaults:
                if c.signed_in_person:
                    schema = ExistingCFPSchema
                else:
                    schema = NewNewCFPSchema

                result, errors = schema().validate(defaults, self.dbsession)
                if not errors:
                    c.proposal = Proposal()
                    # update the objects with the validated form data
                    for k in result['proposal']:
                        setattr(c.proposal, k, result['proposal'][k])

                    if not c.signed_in_person:
                        c.person = model.Person()
                        for k in result['person']:
                            setattr(c.person, k, result['person'][k])
                        self.dbsession.save(c.person)
                    else:
                        c.person = c.signed_in_person
                        for k in result['person']:
                            setattr(c.person, k, result['person'][k])

                    c.person.proposals.append(c.proposal)

                    #if result['attachment'] is not None:
                    #    c.attachment = Attachment()
                    #    for k in result['attachment']:
                    #        setattr(c.attachment, k, result['attachment'][k])
                    #    c.proposal.attachments.append(c.attachment)

                    return render_response('cfp/thankyou.myt')

        return render_response("cfp/new.myt",
                               defaults=defaults, errors=errors)

    def submit_mini(self):

        # call-for-miniconfs now closed
        if c.cfmini_status == 'closed':
            return render_response("cfp/closed_mini.myt")
        elif c.cfmini_status == 'not_open':
            return render_response("cfp/not_open_mini.myt")
        else:
            c.cfptypes = self.dbsession.query(ProposalType).all()
            c.tatypes = self.dbsession.query(AssistanceType).all()

            errors = {}
            defaults = dict(request.POST)

            if request.method == 'POST' and defaults:
                if c.signed_in_person:
                    schema = ExistingMiniSchema
                else:
                    schema = NewNewMiniSchema
                result, errors = schema().validate(defaults, self.dbsession)

                if not errors:
                    c.proposal = Proposal()
                    # update the objects with the validated form data
                    for k in result['proposal']:
                        setattr(c.proposal, k, result['proposal'][k])

                    if not c.signed_in_person:
                        c.person = model.Person()
                        for k in results['person']:
                            setattr(c.person, k, results['person'][k])
                        self.dbsession.save(c.person)
                    else:
                        c.person = c.signed_in_person
                        for k in result['person']:
                            setattr(c.person, k, result['person'][k])

                    c.person.proposals.append(c.proposal)

                    for k in result['person']:
                        setattr(c.person, k, result['person'][k])

                    if result['attachment'] is not None:
                        c.attachment = Attachment()
                        for k in result['attachment']:
                            setattr(c.attachment, k, result['attachment'][k])
                        c.proposal.attachments.append(c.attachment)

                    email((c.person.email_address, 
                              lca_info['mini_conf_email']),
                          render('cfp/thankyou_mini_email.myt', fragment=True))

                    return render_response('cfp/thankyou_mini.myt')

            return render_response("cfp/new_mini.myt",
                                   defaults=defaults, errors=errors)
