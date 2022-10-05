// const { createApp } = Vue;
var testvue2 = Vue.createApp({
    template: '#testvue2',
    delimiters: ["[[", "]]"],
    props: {
        proposalId: {
            type: Number,
        },
    },
    methods: {
       showDiv: function() {
	    if (this.showdiv == true) { 
                  this.showdiv = false;
	    }  else {
                  this.showdiv = true;
            }
       },
    },
    data: function() {
      return {
        message: 'Hello Vue 2 TEST!',
        fullname: "No Name",
	showdiv: false,
	current_time: moment().format("MM ddd, YYYY hh:mm:ss a")
      }
    },
    mounted: function () { 
         console.log("Loading Template 2");
    },
  }).mount("#app2");

