# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Hazard Category

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

# noinspection PyPackageRequirements
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QListWidgetItem

from safe.definitionsv4.layer_purposes import layer_purpose_hazard
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import hazard_category_question
from safe.definitionsv4.utilities import (
    definition, hazard_categories_for_layer)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwHazardCategory(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Hazard Category"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_hazard_category())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_layermode
        return new_step

    def hazard_categories_for_layer(self):
        """Return a list of valid hazard categories for a layer.

        :returns: A list where each value represents a valid hazard category.
        :rtype: list
        """
        if self.parent.step_kw_purpose.\
                selected_purpose() != layer_purpose_hazard:
            return []
        return hazard_categories_for_layer()

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstHazardCategories_itemSelectionChanged(self):
        """Update hazard category description label.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.clear_further_steps()
        # Set widgets
        hazard_category = self.selected_hazard_category()
        # Exit if no selection
        if not hazard_category:
            return
        # Set description label
        self.lblDescribeHazardCategory.setText(hazard_category["description"])
        # Enable the next button
        self.parent.pbnNext.setEnabled(True)

    def selected_hazard_category(self):
        """Obtain the hazard category selected by user.

        :returns: Metadata of the selected hazard category.
        :rtype: dict, None
        """
        item = self.lstHazardCategories.currentItem()
        try:
            return definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def clear_further_steps(self):
        """ Clear all further steps
            in order to properly calculate the prev step
        """
        self.parent.step_kw_layermode.lstLayerModes.clear()
        self.parent.step_kw_unit.lstUnits.clear()
        self.parent.step_kw_field.lstFields.clear()
        self.parent.step_kw_classification.lstClassifications.clear()

    def set_widgets(self):
        """Set widgets on the Hazard Category tab."""
        self.clear_further_steps()
        # Set widgets
        self.lstHazardCategories.clear()
        self.lblDescribeHazardCategory.setText('')
        self.lblSelectHazardCategory.setText(
            hazard_category_question)
        hazard_categories = self.hazard_categories_for_layer()
        for hazard_category in hazard_categories:
            if not isinstance(hazard_category, dict):
                # noinspection PyTypeChecker
                hazard_category = definition(hazard_category)
            # noinspection PyTypeChecker
            item = QListWidgetItem(
                hazard_category['name'],
                self.lstHazardCategories)
            # noinspection PyTypeChecker
            item.setData(QtCore.Qt.UserRole, hazard_category['key'])
            self.lstHazardCategories.addItem(item)

        # Set values based on existing keywords (if already assigned)
        category_keyword = self.parent.get_existing_keyword('hazard_category')
        if category_keyword:
            categories = []
            for index in xrange(self.lstHazardCategories.count()):
                item = self.lstHazardCategories.item(index)
                categories.append(item.data(QtCore.Qt.UserRole))
            if category_keyword in categories:
                self.lstHazardCategories.setCurrentRow(
                    categories.index(category_keyword))

        self.auto_select_one_item(self.lstHazardCategories)
