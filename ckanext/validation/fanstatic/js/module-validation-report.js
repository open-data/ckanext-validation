this.ckan.module('validation-report', function (jQuery) {
  return {
    options: {
      report: null
    },
    initialize: function() {
      frictionlessComponents.render(
        frictionlessComponents.Report,
        {this.options.report},
        this.el[0]
      )
    }
  }
});
