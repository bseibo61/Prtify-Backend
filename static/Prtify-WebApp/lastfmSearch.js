var authDone = false;
var party;
//
$(document).ready(function(){
    // the "href" attribute of the modal trigger must specify the modal ID that wants to be triggered
    $('.modal').modal();
});

$("#searchForm").submit(function(event){
  $('#modal1').modal('open');
  httpGet();
  event.preventDefault();
});

var authDone = false;
var party;

firebase.auth().onAuthStateChanged(function(user) {
  var isAnonymous = user.isAnonymous;
  uid = user.uid;
  var json = getJson();
  found = false;
  for (var u in json.users) {
    if (u == uid) {
      party = json.users[u].party;
      found = true;
    }
  }
  // if (!found) {
  // window.location.assign('index.html');
  // }
  authDone = true;
});

function httpGet(){
  $("#result").empty();
  var songName = $("#search").val();
  var url = "http://ws.audioscrobbler.com/2.0/?method=track.search&track="+songName+"&api_key=a1628eee06b5e44c3e2ba48cf52f07c7&limit=5&format=json"
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open("GET", url, false);

  setTimeout(() =>{}, 3000);

  xmlHttp.send(null);


  // var r = JSON.parse(xmlHttp, results);
  $.getJSON(url, function(data){
    // var artistArr = [10];
    var counter = 0;
    $.each(data.results.trackmatches.track, function(i, item){
      // if($.inArray(item.artist, artistArr)){
        // $('#result').append('<a id='+counter+' >'+'</a>');
        // var string = '[{"#text"}]'
        var id = "pizza";

        $('#result').append('<ul class="collection">'+
        '<li class="collection-item avatar">'+
            '<img src='+item.image[0]['#text']+' alt="" class="circle">'+
            '<span class="title"><b>'+item.name+'</b></span>'+
            '<p>'+item.artist+'<t>'+'<a href="#!" class="secondary-content">'+'<i id='+counter+' class="material-icons">add</i>'+'</a>'+
        '</li>'+
      '</ul>');
      var x = document.getElementById(counter);

        x.addEventListener("click", function(){
            firebase.database().ref("parties/"+party+"/requests/"+id).update({
              name: item.name,
              artist: item.artist,
          });
          var $toastContent = $('<span>New Song!</span>').add($('<button class="btn-flat toast-action" onclick="scrollToBottom()">Scroll to Bottom</button>'));
          Materialize.toast($toastContent, 4000, 'rounded');

        });
        counter = counter + 1;
      // console.log(item);
      // }
      // artistArr[counter] = item.artist;
    });
    // $('#result').append(html);
  });
}

// function test(item){
//   console.log(item);
//   firebase.database().ref("parties/"+party+"/requests/"+item).update({
//     name: item
//   })
// }
