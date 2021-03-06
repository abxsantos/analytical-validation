import json

from flask_restful import Resource, reqparse

from analytical_validation.data_handler.data_handler import DataHandler
from analytical_validation.exceptions import NegativeValue, DataNotSymmetric, DataNotListOfLists, \
    DataNotList, ValueNotValid
from analytical_validation.validators.linearity_validator import LinearityValidator

parser = reqparse.RequestParser()
parser.add_argument('analytical_data')
parser.add_argument('concentration_data')


class Linearity(Resource):

    def post(self):
        args = parser.parse_args()
        print(args)
        input_analytical_data = json.loads(args['analytical_data'])
        input_concentration_data = json.loads(args['concentration_data'])
        try:
            checked_analytical_data, checked_concentration_data = DataHandler(input_analytical_data,
                                                                              input_concentration_data).handle_data()
            linearity_validator = LinearityValidator(checked_analytical_data, checked_concentration_data)
            linearity_validator.validate_linearity()

            return {
                       'regression_coefficients': {'intercept': linearity_validator.intercept,
                                                   'insignificant_intercept': linearity_validator.insignificant_intercept,
                                                   'slope': linearity_validator.slope,
                                                   'significant_slope': linearity_validator.significant_slope,
                                                   'r_squared': linearity_validator.r_squared,
                                                   'valid_regression': linearity_validator.valid_regression_model},
                       'regression_anova': {'sum_of_squares_model': linearity_validator.sum_of_squares_model,
                                            'sum_of_squares_residues': linearity_validator.sum_of_squares_resid,
                                            'sum_of_squares_total': linearity_validator.sum_of_squares_total,
                                            'degrees_of_freedom_model': linearity_validator.degrees_of_freedom_model,
                                            'degrees_of_freedom_residues': linearity_validator.degrees_of_freedom_residues,
                                            'degrees_of_freedom_total': linearity_validator.degrees_of_freedom_total,
                                            'mean_squared_error_model': linearity_validator.mean_squared_error_model,
                                            'mean_squared_error_residues': linearity_validator.mean_squared_error_residues,
                                            'anova_f_value': linearity_validator.anova_f_value,
                                            'anova_f_pvalue': linearity_validator.anova_f_pvalue, },
                       'cleaned_data': {'outliers': linearity_validator.outliers,
                                        'cleaned_analytical_data': linearity_validator.cleaned_analytical_data,
                                        'cleaned_concentration_data': linearity_validator.cleaned_concentration_data},
                       'shapiro_pvalue': linearity_validator.shapiro_pvalue,
                       'breusch_pagan_pvalue': linearity_validator.breusch_pagan_pvalue,
                       'linearity_is_valid': linearity_validator.linearity_is_valid,
                       'regression_residues': linearity_validator.regression_residues,
                       'is_normal_distribution': linearity_validator.is_normal_distribution,
                       'is_homoscedastic': linearity_validator.is_homoscedastic,
                       'durbin_watson_value': linearity_validator.durbin_watson_value,
                       'status': 201}, 201
        except ValueNotValid:
            return {"ValueNotValid": {"body": "Non number values are not valid. Check and try again.",
                                      "status": 400}}, 400
        except DataNotList:
            return {"DataNotListOfLists": {"body": "The given data is not a list of lists.", "status": 400}}, 400
        except DataNotListOfLists:
            return {"DataNotList": {"body": "One of the input data is not a list.", "status": 400}}, 400
        except DataNotSymmetric:
            return {"ValueNotValid": {"body": "Non number values are not valid. Check and try again.",
                                      "status": 400}}, 400
        except NegativeValue:
            return {"NegativeValue": {"body": "Negative values are not valid. Check and try again.",
                                      "status": 400}}, 400
        except AttributeError:
            return {"AttributeError": {
                "body": "There is too few values! Check your inputs and try again.",
                "status": 400}}, 400
        except TypeError:
            return {"TypeError": {"body": "There is something wrong with your values! Check and try again.",
                                  "status": 400}}, 400
