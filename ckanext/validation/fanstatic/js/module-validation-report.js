this.ckan.module('validation-report', function (jQuery) {
  return {
    options: {
      report: null
    },
    initialize: function() {
      goodtablesUI.render(
        goodtablesUI.Report,
        {
          report: this.options.report,
          spec: {
            errors: {
              "io-error": {
                "name": this._("IO Error"),
                "message": this._("The data source returned an IO Error of type {error_type}"),
                "description": this._("Data reading error because of IO error.\n\n How it could be resolved:\n - Fix path if it's not correct.")
              },
              "http-error": {
                "name": this._("HTTP Error"),
                "message": this._("The data source returned an HTTP error with a status code of {status_code}"),
                "description": this._("Data reading error because of HTTP error.\n\n How it could be resolved:\n - Fix url link if it's not correct.")
              },
              "source-error": {
                "name": this._("Source Error"),
                "message": this._("The data source has not supported or has inconsistent contents; no tabular data can be extracted"),
                "description": this._("Data reading error because of not supported or inconsistent contents.\n\n How it could be resolved:\n - Fix data contents (e.g. change JSON data to array or arrays/objects).\n - Set correct source settings in {validator}.")
              },
              "scheme-error": {
                "name": this._("Scheme Error"),
                "message": this._("The data source is in an unknown scheme; no tabular data can be extracted"),
                "description": this._("Data reading error because of incorrect scheme.\n\n How it could be resolved:\n - Fix data scheme (e.g. change scheme from `ftp` to `http`).\n - Set correct scheme in {validator}.")
              },
              "format-error": {
                "name": this._("Format Error"),
                "message": this._("The data source is in an unknown format; no tabular data can be extracted"),
                "description": this._("Data reading error because of incorrect format.\n\n How it could be resolved:\n - Fix data format (e.g. change file extension from `txt` to `csv`).\n - Set correct format in {validator}.")
              },
              "encoding-error": {
                "name": this._("Encoding Error"),
                "message": this._("The data source could not be successfully decoded with {encoding} encoding"),
                "description": this._("Data reading error because of an encoding problem.\n\n How it could be resolved:\n - Fix data source if it's broken.\n - Set correct encoding in {validator}.")
              },
              "blank-header": {
                "name": this._("Blank Header"),
                "message": this._("Header in column {column_number} is blank"),
                "description": this._("A column in the header row is missing a value. Column names should be provided.\n\n How it could be resolved:\n - Add the missing column name to the first row of the data source.\n - If the first row starts with, or ends with a comma, remove it.\n - If this error should be ignored disable `blank-header` check in {validator}.")
              },
              "duplicate-header": {
                "name": this._("Duplicate Header"),
                "message": this._("Header in column {column_number} is duplicated to header in column(s) {column_numbers}"),
                "description": this._("Two columns in the header row have the same value. Column names should be unique.\n\n How it could be resolved:\n - Add the missing column name to the first row of the data.\n - If the first row starts with, or ends with a comma, remove it.\n - If this error should be ignored disable `duplicate-header` check in {validator}.")
              },
              "blank-row": {
                "name": this._("Blank Row"),
                "message": this._("Row {row_number} is completely blank"),
                "description": this._("This row is empty. A row should contain at least one value.\n\n How it could be resolved:\n - Delete the row.\n - If this error should be ignored disable `blank-row` check in {validator}.")
              },
              "duplicate-row": {
                "name": this._("Duplicate Row"),
                "message": this._("Row {row_number} is duplicated to row(s) {row_numbers}"),
                "description": this._("The exact same data has been seen in another row.\n\n How it could be resolved:\n - If some of the data is incorrect, correct it.\n - If the whole row is an incorrect duplicate, remove it.\n - If this error should be ignored disable `duplicate-row` check in {validator}.")
              },
              "extra-value": {
                "name": this._("Extra Value"),
                "message": this._("Row {row_number} has an extra value in column {column_number}"),
                "description": this._("This row has more values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.\n\n How it could be resolved:\n - Check data has an extra comma between the values in this row.\n - If this error should be ignored disable `extra-value` check in {validator}.")
              },
              "missing-value": {
                "name": this._("Missing Value"),
                "message": this._("Row {row_number} has a missing value in column {column_number}"),
                "description": this._("This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.\n\n How it could be resolved:\n - Check data is not missing a comma between the values in this row.\n - If this error should be ignored disable `missing-value` check in {validator}.")
              },
              "schema-error": {
                "name": this._("Table Schema Error"),
                "message": this._("Table Schema error: {error_message}"),
                "description": this._("Provided schema is not valid.\n\n How it could be resolved:\n - Update schema descriptor to be a valid descriptor\n - If this error should be ignored disable schema cheks in {validator}.")
              },
              "non-matching-header": {
                "name": this._("Non-Matching Header"),
                "message": this._("Header in column {column_number} doesn't match field name {field_name} in the schema"),
                "description": this._("One of the data source headers doesn't match the field name defined in the schema.\n\n How it could be resolved:\n - Rename header in the data source or field in the schema\n - If this error should be ignored disable `non-matching-header` check in {validator}.")
              },
              "extra-header": {
                "name": this._("Extra Header"),
                "message": this._("There is an extra header in column {column_number}"),
                "description": this._("The first row of the data source contains header that doesn't exist in the schema.\n\n How it could be resolved:\n - Remove the extra column from the data source or add the missing field to the schema\n - If this error should be ignored disable `extra-header` check in {validator}.")
              },
              "missing-header": {
                "name": this._("Missing Header"),
                "message": this._("There is a missing header in column {column_number}"),
                "description": this._("Based on the schema there should be a header that is missing in the first row of the data source.\n\n How it could be resolved:\n - Add the missing column to the data source or remove the extra field from the schema\n - If this error should be ignored disable `missing-header` check in {validator}.")
              },
              "type-or-format-error": {
                "name": this._("Type or Format Error"),
                "message": this._("The value {value} in row {row_number} and column {column_number} is not type {field_type} and format {field_format}"),
                "description": this._("The value does not match the schema type and format for this field.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If this value is correct, adjust the type and/or format.\n - To ignore the error, disable the `type-or-format-error` check in {validator}. In this case all schema checks for row values will be ignored.")
              },
              "required-constraint": {
                "name": this._("Required Constraint"),
                "message": this._("Column {column_number} is a required field, but row {row_number} has no value"),
                "description": this._("This field is a required field, but it contains no value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove the `required` constraint from the schema.\n - If this error should be ignored disable `required-constraint` check in {validator}.")
              },
              "pattern-constraint": {
                "name": this._("Pattern Constraint"),
                "message": this._("The value {value} in row {row_number} and column {column_number} does not conform to the pattern constraint of {constraint}"),
                "description": this._("This field value should conform to constraint pattern.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `pattern` constraint in the schema.\n - If this error should be ignored disable `pattern-constraint` check in {validator}.")
              },
              "unique-constraint": {
                "name": this._("Unique Constraint"),
                "message": this._("Rows {row_numbers} has unique constraint violation in column {column_number}"),
                "description": this._("This field is a unique field but it contains a value that has been used in another row.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then the values in this column are not unique. Remove the `unique` constraint from the schema.\n - If this error should be ignored disable `unique-constraint` check in {validator}.")
              },
              "enumerable-constraint": {
                "name": this._("Enumerable Constraint"),
                "message": this._("The value {value} in row {row_number} and column {column_number} does not conform to the given enumeration: {constraint}"),
                "description": this._("This field value should be equal to one of the values in the enumeration constraint.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `enum` constraint in the schema.\n - If this error should be ignored disable `enumerable-constraint` check in {validator}.")
              },
              "minimum-constraint": {
                "name": this._("Minimum Constraint"),
                "message": this._("The value {value} in row {row_number} and column {column_number} does not conform to the minimum constraint of {constraint}"),
                "description": this._("This field value should be greater or equal than constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `minimum` constraint in the schema.\n - If this error should be ignored disable `minimum-constraint` check in {validator}.")
              },
              "maximum-constraint": {
                "name": this._("Maximum Constraint"),
                "message": this._("The value {value} in row {row_number} and column {column_number} does not conform to the maximum constraint of {constraint}"),
                "description": this._("This field value should be less or equal than constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `maximum` constraint in the schema.\n - If this error should be ignored disable `maximum-constraint` check in {validator}.")
              },
              "minimum-length-constraint": {
                "name": this._("Minimum Length Constraint"),
                "message": this._("The value {value} in row {row_number} and column {column_number} does not conform to the minimum length constraint of {constraint}"),
                "description": this._("A lenght of this field value should be greater or equal than schema constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `minimumLength` constraint in the schema.\n - If this error should be ignored disable `minimum-length-constraint` check in {validator}.")
              },
              "maximum-length-constraint": {
                "name": this._("Maximum Length Constraint"),
                "message": this._("The value {value} in row {row_number} and column {column_number} does not conform to the maximum length constraint of {constraint}"),
                "description": this._("A lenght of this field value should be less or equal than schema constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `maximumLength` constraint in the schema.\n - If this error should be ignored disable `maximum-length-constraint` check in {validator}.")
              }
	    }
          }
        },
        this.el[0]
      )
    }
  }
});
