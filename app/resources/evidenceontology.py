__author__ = 'andreap'
from flask import current_app
from flask.ext import restful
from flask.ext.restful import abort
from flask_restful_swagger import swagger


class EcoLabelFromCode(restful.Resource):


    @swagger.operation(
        notes='''test with  ECO:0000317 ''',)
    def get(self, code ):
        es = current_app.extensions['esquery']
        res = es.get_label_for_eco_code(code)
        if not res:
            abort(404, message="ECO ID %s cannot be found"%code)
        return res