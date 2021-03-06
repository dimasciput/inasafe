# coding=utf-8
from safe.definitionsv4.exposure import exposure_all
from safe.definitionsv4.fields import (
    exposure_type_field,
    exposure_class_field,
    hazard_count_field,
    total_affected_field,
    total_unaffected_field,
    total_field)
from safe.definitionsv4.hazard_classifications import all_hazard_classes
from safe.reportv4.extractors.util import layer_definition_type
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = ':%H$'


def analysis_detail_extractor(impact_report, component_metadata):
    """
    Extracting analysis result from the impact layer

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.reportv4.report_metadata.ReportMetadata

    :return: context for rendering phase
    :rtype: dict
    """
    context = {}

    hazard_layer = impact_report.hazard
    exposure_layer = impact_report.exposure
    analysis_layer = impact_report.analysis
    analysis_layer_fields = analysis_layer.keywords['inasafe_fields']
    analysis_feature = analysis_layer.getFeatures().next()
    exposure_breakdown = impact_report.exposure_breakdown
    exposure_breakdown_fields = exposure_breakdown.keywords['inasafe_fields']

    """Initializations"""

    # Get hazard classification
    hazard_classification = None
    # retrieve hazard classification from hazard layer
    for classification in all_hazard_classes:
        classification_name = hazard_layer.keywords['classification']
        if classification_name == classification['key']:
            hazard_classification = classification
            break

    # Get exposure type definition
    exposure_type = layer_definition_type(exposure_layer)

    # Analysis detail only applicable for breakable exposure types:
    itemizable_exposures_all = [
        exposure for exposure in exposure_all
        if exposure.get('classifications')]
    if exposure_type not in itemizable_exposures_all:
        return context

    # Get breakdown field
    breakdown_field = None
    # I'm not sure what's the difference
    # It is possible to have exposure_type_field or exposure_class_field
    # at the moment
    breakdown_fields = [
        exposure_type_field,
        exposure_class_field
    ]
    for field in breakdown_fields:
        if field['key'] in exposure_breakdown_fields:
            breakdown_field = field
            break

    """Create detail header"""
    headers = []

    # breakdown header
    breakdown_header_template = ''
    if breakdown_field == exposure_type_field:
        # TODO: should move this translation somewhere in definitions
        breakdown_header_template = tr('%(exposure)s type')
    elif breakdown_field == exposure_class_field:
        breakdown_header_template = tr('%(exposure)s class')

    headers.append(
        breakdown_header_template % {
            'exposure': exposure_type['name']
        })

    # hazard header
    for hazard_class in hazard_classification['classes']:
        headers.append(hazard_class['name'])

    # affected, unaffected, total header
    report_fields = [
        total_affected_field,
        total_unaffected_field,
        total_field
    ]
    for report_field in report_fields:
        headers.append(report_field['name'])

    """Create detail rows"""
    details = []
    for feat in exposure_breakdown.getFeatures():
        row = []

        # Get breakdown name
        breakdown_field_name = breakdown_field['field_name']
        field_index = exposure_breakdown.fieldNameIndex(breakdown_field_name)
        breakdown_name = feat[field_index]
        row.append(breakdown_name)

        # Get hazard count
        for hazard_class in hazard_classification['classes']:
            # hazard_count_field is a dynamic field with hazard class
            # as parameter
            field_key_name = hazard_count_field['key'] % (
                hazard_class['key'], )

            try:
                # retrieve dynamic field name from analysis_fields keywords
                # will cause key error if no hazard count for that particular
                # class
                field_name = exposure_breakdown_fields[field_key_name]
                field_index = exposure_breakdown.fieldNameIndex(field_name)
                count_value = feat[field_index]
                row.append(count_value)
            except KeyError:
                # in case the field was not found
                # assume value 0
                row.append(0)

        # Get Affected count
        field_index = exposure_breakdown.fieldNameIndex(
            total_affected_field['field_name'])
        total_affected = feat[field_index]
        row.append(total_affected)

        # Get Unaffected count
        field_index = exposure_breakdown.fieldNameIndex(
            total_unaffected_field['field_name'])
        total_unaffected = feat[field_index]
        row.append(total_unaffected)

        # Get Total count
        field_index = exposure_breakdown.fieldNameIndex(
            total_field['field_name'])
        total = feat[field_index]
        row.append(total)

        details.append(row)

    """create total footers"""
    # create total header
    footers = [total_field['name']]
    # total for hazard
    for hazard_class in hazard_classification['classes']:
        # hazard_count_field is a dynamic field with hazard class
        # as parameter
        field_key_name = hazard_count_field['key'] % (
            hazard_class['key'],)

        try:
            # retrieve dynamic field name from analysis_fields keywords
            # will cause key error if no hazard count for that particular
            # class
            field_name = analysis_layer_fields[field_key_name]
            field_index = analysis_layer.fieldNameIndex(field_name)
            count_value = analysis_feature[field_index]
            footers.append(count_value)
        except KeyError:
            # in case the field was not found
            # assume value 0
            footers.append(0)
    # total for affected
    field_index = analysis_layer.fieldNameIndex(
        total_affected_field['field_name'])
    total_affected = analysis_feature[field_index]
    footers.append(total_affected)

    # total Unaffected count
    field_index = analysis_layer.fieldNameIndex(
        total_unaffected_field['field_name'])
    total_unaffected = analysis_feature[field_index]
    footers.append(total_unaffected)

    # total count
    field_index = analysis_layer.fieldNameIndex(
        total_field['field_name'])
    total = analysis_feature[field_index]
    footers.append(total)

    context['header'] = tr('Estimated number of %(exposure)s by type') % {
        'exposure': exposure_type['name']
    }
    context['detail_table'] = {
        'headers': headers,
        'details': details,
        'footers': footers,
    }

    return context
