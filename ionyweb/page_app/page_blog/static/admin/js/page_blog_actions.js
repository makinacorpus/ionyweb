admin.page_blog = {

    edit_entries: function(relation_id){
		admin.GET({
		    url : '/wa/action/' + relation_id + '/entry_list/',
		});
    },


};
