/**
 * Created by satya on 11/5/17.
 */
function modalClicked(){
  $('#modal1').modal('open');
}

function toastClicked() {
    var $toastContent = $('<span>New Song Added!</span>').add($('<button class="btn-flat toast-action" onclick="scrollToBottom()">Scroll to Bottom</button>'));
    Materialize.toast($toastContent, 4000, 'rounded');
}

function scrollToBottom() {
    var toastElement = $('.toast').first()[0];
    var toastInstance = toastElement.M_Toast;
    toastInstance.remove();
    window.scrollTo(0,document.body.scrollHeight);
}

$('.modal').modal();
