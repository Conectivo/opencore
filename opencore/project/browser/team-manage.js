jQuery.noConflict();

function getMemberId(rowEl) {
  var row = jQuery(rowEl).closest("tr");
  var id = row.attr('id');
  return id;
};

function buildForm(memId, memberRole) {
  var action;
  if( memberRole == "administrator" ) {
    action = "demote-admin";
  } else {
    action = "promote-admin";
  };

  var html = "<select name='" + memId + "_role' id='" + memId + "_role'>";
  if( memberRole == "administrator" ) {
    html += "<option value='ProjectAdmin' selected='true'>administrator</option>";
    html += "<option value='ProjectMember'>member</option>";
  } else {
    html += "<option value='ProjectAdmin'>administrator</option>";
    html += "<option value='ProjectMember' selected='true'>member</option>";
  };
  html += "</select>";
  html += "<input style='display:none;' type='submit' value='go' name='task|" + memId + "|" + action + "' />";
  return html;
};

jQuery(document).ready(function() {
	jQuery("tbody#mship-rows td.role div").live("click", function() {
		var memberRole = jQuery(this).attr("class");
		jQuery(this).replaceWith(buildForm(getMemberId(this), memberRole));
	    });

	jQuery("tbody#mship-rows td.role select").live("change", function() {
		jQuery(this).siblings("input[type='submit']").click();
	    });

    });
