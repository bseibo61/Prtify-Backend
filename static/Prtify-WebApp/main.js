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
  //   window.location.assign('index.html');
  // }
  authDone = true;
});


setTimeout(function() {
  $('#headerQueue').text(party + " Queue");
  var partyRef = firebase.database().ref('parties/' + party + '/queue');
  partyRef.on('value', function(snapshot) {
    var info = snapshot.val();
    if(info != null){
      console.log(info);
      var songList = [];
      for (var song in info) {
        info[song].total = info[song].upvotes - info[song].downvotes;
        songList.push(info[song]);
      }
      songList.sort();
      songList.sort(function(a, b) {
        var x = b.total - a.total;
        return x;
      });
      for(var curr in info){
        firebase.database().ref("parties/" + party + "/queue/" + info[curr].key).update({
          votes: info[curr].total
        });
      }
      $('#queue').empty();
      for (var n in songList) {
        var gaveUp = "0.5";
        var gaveDown = "0.5";
        if(songList[n].upvoted != null && uid in songList[n].upvoted){
          gaveUp = "1";
        }else if (songList[n].downvoted != null && uid in songList[n].downvoted) {
          gaveDown = "1";
        }
        // $("#queue").append('<li><p>'+songList[n].name+'</p><p>'+songList[n].artist+'</p><p>'+songList[n].image+'</p><button value="'+songList[n].name+'" onclick="upvote(this.value)">Upvote</button><button value="'+songList[n].name+'" onclick="downvote(this.value)">Downvote</button></li>');
        $('#queue').append('<li class="collection-item avatar"> \
          <img src="' + songList[n].image + '" alt="" class="circle"> \
          <span class="title"><b>' + songList[n].name + '</b></span> \
          <p>' + songList[n].album + ' <br>' + songList[n].artist + '<br> \
          </p> \
          <a href="#!" class="secondary-content"> \
            <div> \
              <div> \
                <i class="material-icons" style="opacity: '+gaveUp+'" value="up" id="' + songList[n].key+"up" + '" >arrow_upward</i><i class="material-icons" value="' + songList[n].name + '" id="' + songList[n].key + '" style="opacity: '+gaveDown+'">arrow_downward</i> \
              </div> \
              <div> \
                <p class="center" style="font-size: large"><b>' + songList[n].total + '</b></p> \
              </div> \
            </div> \
          </a> \
        </li>');
        var up = document.getElementById(songList[n].key+"up");
        up.addEventListener("click", function() {
          var json = getJson();
          listenSong = $(this).attr('id');
          listenSong = listenSong.slice(0,-2);
          var downvotes = json.parties[party].queue[listenSong].downvotes - 1;
          var upvotes = json.parties[party].queue[listenSong].upvotes + 1;
          var alreadyVoted = false;
          for (u in json.parties[party].queue[listenSong].upvoted) {
            if (json.parties[party].queue[listenSong].upvoted[u].uid == uid) {
              alreadyVoted = true;
            }
          }
          for (u in json.parties[party].queue[listenSong].downvoted) {
            if (json.parties[party].queue[listenSong].downvoted[u].uid == uid) {
              alreadyVoted = true;
              firebase.database().ref("parties/" + party + "/queue/" + listenSong).update({
                downvotes: downvotes
              });
              firebase.database().ref("parties/" + party + "/queue/" + listenSong + "/downvoted/" + uid).remove()
                .then(function() {
                  console.log("sucess");
                })
                .catch(function(error) {
                  console.log("Remove failed: " + error.message)
                });
              alreadyVoted = false;
            }
          }
          if (!alreadyVoted) {
            firebase.database().ref("parties/" + party + "/queue/" + listenSong).update({
              upvotes: upvotes
            });
            firebase.database().ref("parties/" + party + "/queue/" + listenSong + "/upvoted/" + uid).update({
              uid: uid
            });
          }else{
            firebase.database().ref("parties/" + party + "/queue/" + listenSong).update({
              upvotes: upvotes - 2
            });
            firebase.database().ref("parties/" + party + "/queue/" + listenSong + "/upvoted/" + uid).remove()
              .then(function() {
                console.log("sucess");
              })
              .catch(function(error) {
                console.log("Remove failed: " + error.message)
              });
          }

        });





        var down = document.getElementById(songList[n].key);
        down.addEventListener("click", function() {
          var json = getJson();
          listenSong = $(this).attr('id');
          var upvotes = json.parties[party].queue[listenSong].upvotes - 1;
          var downvotes = json.parties[party].queue[listenSong].downvotes + 1;
          var alreadyVoted = false;
          for (u in json.parties[party].queue[listenSong].downvoted) {
            if (json.parties[party].queue[listenSong].downvoted[u].uid == uid) {
              alreadyVoted = true;
            }
          }
          for (u in json.parties[party].queue[listenSong].upvoted) {
            if (json.parties[party].queue[listenSong].upvoted[u].uid == uid) {
              alreadyVoted = true;
              firebase.database().ref("parties/" + party + "/queue/" + listenSong).update({
                upvotes: upvotes
              });
              firebase.database().ref("parties/" + party + "/queue/" + listenSong + "/upvoted/" + uid).remove()
                .then(function() {
                  console.log("sucess");
                })
                .catch(function(error) {
                  console.log("Remove failed: " + error.message)
                });
              alreadyVoted = false;
            }
          }
          if (!alreadyVoted) {
            firebase.database().ref("parties/" + party + "/queue/" + listenSong).update({
              downvotes: downvotes
            });
            firebase.database().ref("parties/" + party + "/queue/" + listenSong + "/downvoted/" + uid).update({
              uid: uid
            });
          }else{
            firebase.database().ref("parties/" + party + "/queue/" + listenSong).update({
              downvotes: downvotes - 2
            });
            firebase.database().ref("parties/" + party + "/queue/" + listenSong + "/downvoted/" + uid).remove()
              .then(function() {
                console.log("sucess");
              })
              .catch(function(error) {
                console.log("Remove failed: " + error.message)
              });
          }

        });
      }
    }

  });
}, 1000);

function downvote(song) {
  var json = getJson();
  var downvotes = json.parties[party].queue[song].downvotes + 1;
  var upvotes = json.parties[party].queue[song].upvotes - 1;
  var alreadyVoted = false;
  for (u in json.parties[party].queue[song].downvoted) {
    if (json.parties[party].queue[song].downvoted[u].uid == uid) {
      alreadyVoted = true;
    }
  }
  for (u in json.parties[party].queue[song].upvoted) {
    if (json.parties[party].queue[song].upvoted[u].uid == uid) {
      alreadyVoted = true;
      firebase.database().ref("parties/" + party + "/queue/" + song).update({
        upvotes: upvotes
      });
      firebase.database().ref("parties/" + party + "/queue/" + song + "/upvoted/" + uid).remove()
        .then(function() {
          console.log("sucess");
        })
        .catch(function(error) {
          console.log("Remove failed: " + error.message)
        });
      alreadyVoted = false;
    }
  }
  if (!alreadyVoted) {
    firebase.database().ref("parties/" + party + "/queue/" + song).update({
      downvotes: downvotes
    });
    firebase.database().ref("parties/" + party + "/queue/" + song + "/downvoted/" + uid).update({
      uid: uid
    });
  }
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
