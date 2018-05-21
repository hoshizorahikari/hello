//回到顶部
$(window).scroll(function () {
    let h = 600; // 滚动小于600隐藏,大于600显示
    $('#to-top').hide();
    if ($(window).scrollTop() >= h) {
        $('#to-top').show();
    };
});
$("#to-top").click(function () {
    let speed = 400; // 滑动的速度
    $('body,html').animate({
        scrollTop: 0
    }, speed);
    return false;
});