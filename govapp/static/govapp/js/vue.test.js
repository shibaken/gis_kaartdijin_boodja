// const { createApp } = Vue;
var testvue = Vue.createApp({
    template: '#testvue',
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
       giveData: function() {
          testvue2.fullname = this.first_name+' '+this.last_name;	    

       }
    },
    data: function() {
      return {
        message: 'Hello Vue TEST!',
        first_name: "John",
        last_name: "Bloggs",
	showdiv: false,
	current_time: moment().format("MM ddd, YYYY hh:mm:ss a")
      }
    },
    mounted: function () { 
         console.log("Loading Template");

    },
  }).mount("#app");

