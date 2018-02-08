var ref = firebase.database().ref("/rooms");
var uid;
var database = firebase.database();
firebase.auth().onAuthStateChanged(function(user) {
  if (user) {
    var isAnonymous = user.isAnonymous;
    uid = user.uid;
    json = getJson();
    for(var u in json.users){
      if(u == uid && json.users[u].party != null){
        window.location.assign('main.html');
      }
    }
  } else {
    //signed out
  }
});


function joinParty(){
  var party = $("#partyName").val();
  var json = getJson();
  var partyExists = false;
  for(var p in json.parties){
    if(party == p){
      firebase.database().ref("parties/"+party+"/users/"+uid).update({
        uid: uid
      });
      firebase.database().ref("users/"+uid).update({
        uid: uid,
        party: party
      });
      window.location.assign(main.html);
    }
  }
  $("#invalidParty").show();

}

//returns a JSON of the database using REST API
function getJson() {
  var xhttp = new XMLHttpRequest();

  //TODO: IMPORTANT: before putting this on the website, change rules and put some
  //form of authentication in the url
  xhttp.open("GET", "https://voteify.firebaseio.com/.json?print=pretty", false);
  xhttp.send();
  var response = JSON.parse(xhttp.responseText);
  return response;
}
