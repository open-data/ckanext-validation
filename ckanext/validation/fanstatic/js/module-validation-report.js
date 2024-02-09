this.ckan.module('validation-report', function (jQuery) {
  return {
    options: {
      report: null
    },
    initialize: function() {
      const spec = goodtablesUI.spec;
      spec['errors']['io-error'].name = this._("IO Error");
      spec['errors']['io-error'].message = this._("The data source returned an IO Error of type {error_type}");
      spec['errors']['io-error'].description = this._("Data reading error because of IO error.\n\n How it could be resolved:\n - Fix path if it's not correct.");

      spec['errors']['http-error'].name = this._("HTTP Error");
      spec['errors']['http-error'].message = this._("The data source returned an HTTP error with a status code of {status_code}");
      spec['errors']['http-error'].description = this._("Data reading error because of HTTP error.\n\n How it could be resolved:\n - Fix url link if it's not correct.");
      spec['errors']['source-error'].name = this._("Source Error");
      spec['errors']['source-error'].message = this._("The data source has not supported or has inconsistent contents; no tabular data can be extracted");
      spec['errors']['source-error'].description = this._("Data reading error because of not supported or inconsistent contents.\n\n How it could be resolved:\n - Fix data contents (e.g. change JSON data to array or arrays/objects).\n - Set correct source settings in {validator}.");
      spec['errors']['scheme-error'].name = this._("Scheme Error");
      spec['errors']['scheme-error'].message = this._("The data source is in an unknown scheme; no tabular data can be extracted");
      spec['errors']['scheme-error'].description = this._("Data reading error because of incorrect scheme.\n\n How it could be resolved:\n - Fix data scheme (e.g. change scheme from `ftp` to `http`).\n - Set correct scheme in {validator}.");
      spec['errors']['format-error'].name = this._("Format Error");
      spec['errors']['format-error'].message = this._("The data source is in an unknown format; no tabular data can be extracted");
      spec['errors']['format-error'].description = this._("Data reading error because of incorrect format.\n\n How it could be resolved:\n - Fix data format (e.g. change file extension from `txt` to `csv`).\n - Set correct format in {validator}.");
      spec['errors']['encoding-error'].name = this._("Encoding Error");
      spec['errors']['encoding-error'].message = this._("The data source could not be successfully decoded with {encoding} encoding");
      spec['errors']['encoding-error'].description = this._("Data reading error because of an encoding problem.\n\n How it could be resolved:\n - Fix data source if it's broken.\n - Set correct encoding in {validator}.");
      spec['errors']['blank-header'].name = this._("Blank Header");
      spec['errors']['blank-header'].message = this._("Header in column {column_number} is blank");
      spec['errors']['blank-header'].description = this._("A column in the header row is missing a value. Column names should be provided.\n\n How it could be resolved:\n - Add the missing column name to the first row of the data source.\n - If the first row starts with, or ends with a comma, remove it.\n - If this error should be ignored disable `blank-header` check in {validator}.");
      spec['errors']['duplicate-header'].name = this._("Duplicate Header");
      spec['errors']['duplicate-header'].message = this._("Header in column {column_number} is duplicated to header in column(s) {column_numbers}");
      spec['errors']['duplicate-header'].description = this._("Two columns in the header row have the same value. Column names should be unique.\n\n How it could be resolved:\n - Add the missing column name to the first row of the data.\n - If the first row starts with, or ends with a comma, remove it.\n - If this error should be ignored disable `duplicate-header` check in {validator}.");
      spec['errors']['blank-row'].name = this._("Blank Row");
      spec['errors']['blank-row'].message = this._("Row {row_number} is completely blank");
      spec['errors']['blank-row'].description = this._("This row is empty. A row should contain at least one value.\n\n How it could be resolved:\n - Delete the row.\n - If this error should be ignored disable `blank-row` check in {validator}.");
      spec['errors']['duplicate-row'].name = this._("Duplicate Row");
      spec['errors']['duplicate-row'].message = this._("Row {row_number} is duplicated to row(s) {row_numbers}");
      spec['errors']['duplicate-row'].description = this._("The exact same data has been seen in another row.\n\n How it could be resolved:\n - If some of the data is incorrect, correct it.\n - If the whole row is an incorrect duplicate, remove it.\n - If this error should be ignored disable `duplicate-row` check in {validator}.");
      spec['errors']['extra-value'].name = this._("Extra Value");
      spec['errors']['extra-value'].message = this._("Row {row_number} has an extra value in column {column_number}");
      spec['errors']['extra-value'].description = this._("This row has more values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.\n\n How it could be resolved:\n - Check data has an extra comma between the values in this row.\n - If this error should be ignored disable `extra-value` check in {validator}.");
      spec['errors']['missing-value'].name = this._("Missing Value");
      spec['errors']['missing-value'].message = this._("Row {row_number} has a missing value in column {column_number}");
      spec['errors']['missing-value'].description = this._("This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.\n\n How it could be resolved:\n - Check data is not missing a comma between the values in this row.\n - If this error should be ignored disable `missing-value` check in {validator}.");
      spec['errors']['schema-error'].name = this._("Table Schema Error");
      spec['errors']['schema-error'].message = this._("Table Schema error: {error_message}");
      spec['errors']['schema-error'].description = this._("Provided schema is not valid.\n\n How it could be resolved:\n - Update schema descriptor to be a valid descriptor\n - If this error should be ignored disable schema cheks in {validator}.");
      spec['errors']['non-matching-header'].name = this._("Non-Matching Header");
      spec['errors']['non-matching-header'].message = this._("Header in column {column_number} doesn't match field name {field_name} in the schema");
      spec['errors']['non-matching-header'].description = this._("One of the data source headers doesn't match the field name defined in the schema.\n\n How it could be resolved:\n - Rename header in the data source or field in the schema\n - If this error should be ignored disable `non-matching-header` check in {validator}.");
      spec['errors']['extra-header'].name = this._("Extra Header");
      spec['errors']['extra-header'].message = this._("There is an extra header in column {column_number}");
      spec['errors']['extra-header'].description = this._("The first row of the data source contains header that doesn't exist in the schema.\n\n How it could be resolved:\n - Remove the extra column from the data source or add the missing field to the schema\n - If this error should be ignored disable `extra-header` check in {validator}.");
      spec['errors']['missing-header'].name = this._("Missing Header");
      spec['errors']['missing-header'].message = this._("There is a missing header in column {column_number}");
      spec['errors']['missing-header'].description = this._("Based on the schema there should be a header that is missing in the first row of the data source.\n\n How it could be resolved:\n - Add the missing column to the data source or remove the extra field from the schema\n - If this error should be ignored disable `missing-header` check in {validator}.");
      spec['errors']['type-or-format-error'].name = this._("Type or Format Error");
      spec['errors']['type-or-format-error'].message = this._("The value {value} in row {row_number} and column {column_number} is not type {field_type} and format {field_format}");
      spec['errors']['type-or-format-error'].description = this._("The value does not match the schema type and format for this field.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If this value is correct, adjust the type and/or format.\n - To ignore the error, disable the `type-or-format-error` check in {validator}. In this case all schema checks for row values will be ignored.");
      spec['errors']['required-constraint'].name = this._("Required Constraint");
      spec['errors']['required-constraint'].message = this._("Column {column_number} is a required field, but row {row_number} has no value");
      spec['errors']['required-constraint'].description = this._("This field is a required field, but it contains no value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove the `required` constraint from the schema.\n - If this error should be ignored disable `required-constraint` check in {validator}.");
      spec['errors']['pattern-constraint'].name = this._("Pattern Constraint");
      spec['errors']['pattern-constraint'].message = this._("The value {value} in row {row_number} and column {column_number} does not conform to the pattern constraint of {constraint}");
      spec['errors']['pattern-constraint'].description = this._("This field value should conform to constraint pattern.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `pattern` constraint in the schema.\n - If this error should be ignored disable `pattern-constraint` check in {validator}.");
      spec['errors']['unique-constraint'].name = this._("Unique Constraint");
      spec['errors']['unique-constraint'].message = this._("Rows {row_numbers} has unique constraint violation in column {column_number}");
      spec['errors']['unique-constraint'].description = this._("This field is a unique field but it contains a value that has been used in another row.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then the values in this column are not unique. Remove the `unique` constraint from the schema.\n - If this error should be ignored disable `unique-constraint` check in {validator}.");
      spec['errors']['enumerable-constraint'].name = this._("Enumerable Constraint");
      spec['errors']['enumerable-constraint'].message = this._("The value {value} in row {row_number} and column {column_number} does not conform to the given enumeration: {constraint}");
      spec['errors']['enumerable-constraint'].description = this._("This field value should be equal to one of the values in the enumeration constraint.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `enum` constraint in the schema.\n - If this error should be ignored disable `enumerable-constraint` check in {validator}.");
      spec['errors']['minimum-constraint'].name = this._("Minimum Constraint");
      spec['errors']['minimum-constraint'].message = this._("The value {value} in row {row_number} and column {column_number} does not conform to the minimum constraint of {constraint}");
      spec['errors']['minimum-constraint'].description = this._("This field value should be greater or equal than constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `minimum` constraint in the schema.\n - If this error should be ignored disable `minimum-constraint` check in {validator}.");
      spec['errors']['maximum-constraint'].name = this._("Maximum Constraint");
      spec['errors']['maximum-constraint'].message = this._("The value {value} in row {row_number} and column {column_number} does not conform to the maximum constraint of {constraint}");
      spec['errors']['maximum-constraint'].description = this._("This field value should be less or equal than constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `maximum` constraint in the schema.\n - If this error should be ignored disable `maximum-constraint` check in {validator}.");
      spec['errors']['minimum-length-constraint'].name = this._("Minimum Length Constraint");
      spec['errors']['minimum-length-constraint'].message = this._("The value {value} in row {row_number} and column {column_number} does not conform to the minimum length constraint of {constraint}");
      spec['errors']['minimum-length-constraint'].description = this._("A lenght of this field value should be greater or equal than schema constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `minimumLength` constraint in the schema.\n - If this error should be ignored disable `minimum-length-constraint` check in {validator}.");
      spec['errors']['maximum-length-constraint'].name = this._("Maximum Length Constraint");
      spec['errors']['maximum-length-constraint'].message = this._("The value {value} in row {row_number} and column {column_number} does not conform to the maximum length constraint of {constraint}");
      spec['errors']['maximum-length-constraint'].description = this._("A lenght of this field value should be less or equal than schema constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `maximumLength` constraint in the schema.\n - If this error should be ignored disable `maximum-length-constraint` check in {validator}.");
      // (canada fork only): custom specs for DataStore header errors
      spec['errors']['datastore-invalid-header'] = {
        "name": this._("Invalid Header for DataStore"),
        "message": this._("Column name {value} in column {column_number} is not valid for a DataStore header"),
        "description": this._("Column name is invalid for a DataStore header.\n\n How it could be resolved:\n - Remove any leading underscores('_') from the column name.\n - Remove any leading for trailing white space from the column name.\n - Remove any double quotes('\"') from the column name.\n - Make sure the column name is not blank."),
        "type": "custom",
        "context": "head",
        "weight": 7
      };
      spec['errors']['datastore-header-too-long'] = {
        "name": this._("Header Too Long for DataStore"),
        "message": this._("Column name {value} in column {column_number} is too long for a DataStore header"),
        "description": this._("Column name is too long for a DataStore header.\n\n How it could be resolved:\n - Make the column name at most 63 characters long."),
        "type": "custom",
        "context": "head",
        "weight": 7
      };
      goodtablesUI.render(
        goodtablesUI.Report,
        {
          report: this.options.report,
          spec: spec
        },
        this.el[0]
      )
    $(".collapsed").removeClass( "collapsed" );
    $(".collapse").addClass("show");
    }
  }
});
