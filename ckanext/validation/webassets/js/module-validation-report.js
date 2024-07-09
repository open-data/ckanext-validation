"use strict";

ckan.module('validation-report', function (jQuery) {
  return {
    options: {
      report: null
    },
    initialize: function() {
      let element = document.getElementById('report')
      let report = this.options.report
      // (canada fork only): parse report into object
      if( typeof report != 'undefined' && report.length > 0 ){
        report = JSON.parse(report)
      }
      frictionlessComponents.render(frictionlessComponents.Report, { report }, element)
    }
  }
});
