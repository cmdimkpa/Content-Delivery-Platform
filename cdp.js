// CDP client library

const db_base_url = 'https://s3appdb.herokuapp.com/ods/';
const fetch_records_url = db_base_url + 'fetch_records';
const new_record_url = db_base_url + 'new_record';
const delete_url = db_base_url + 'delete_records';
const update_url = db_base_url + 'update_records';

// generate navbar
const generate_navbar = (assets) => {
    var navbar = ""; var i = 0;
    assets.forEach((asset) => {
        i++;
        if (asset.label.length > 30) {
            asset.label = asset.label.slice(0, 27) + "...";
        }
        navbar += `<ul><div onmouseover=showActions('${asset.ContentModel_id}') onmouseleave=hideActions('${asset.ContentModel_id}')><button type="submit" class="button" id="${asset.ContentModel_id}" data-label="${asset.label}" data-url="${asset.url}" onclick=load_asset_on_click('${asset.ContentModel_id}')><span class="button button-inner">${i}</span>${asset.label}</button><br><span id="${asset.ContentModel_id}up" title="move item up" class="button actions" onclick=adjust_asset_position('${asset.ContentModel_id}',1)>u</span><span id="${asset.ContentModel_id}down"  title="move item down" class="button actions" onclick=adjust_asset_position('${asset.ContentModel_id}',-1)>d</span><span id="${asset.ContentModel_id}a"  title="add new item above" class="button actions" data-toggle="modal" data-target="#myModal" onclick=postref(${asset.ref},${assets.length})>a</span><span id="${asset.ContentModel_id}x"  title="delete item" class="button actions" onclick=remove_asset('${asset.ContentModel_id}')>x</span></div></ul>`
    });
    return navbar;
}

const showActions = (asset_id) => {
    if (window.location.href.includes("edit")) {
        $(`#${asset_id}up`).show();
        $(`#${asset_id}down`).show();
        $(`#${asset_id}x`).show();
        $(`#${asset_id}a`).show();
    }
}

const hideActions = (asset_id) => {
    $(`#${asset_id}up`).hide();
    $(`#${asset_id}down`).hide();
    $(`#${asset_id}x`).hide();
    $(`#${asset_id}a`).hide();
}

const display_active = (active_label, active_url) => {
    $("#ActiveLabel").text(active_label);
    $("#ContentIframe").attr('src', active_url);
}

const printableView = () => {
    var active_url = $("#ContentIframe").attr('src');
    window.open(active_url);
}

// load asset on click
const load_asset_on_click = (asset_id) => {
    var active_label = $(`#${asset_id}`).data('label');
    var active_url = $(`#${asset_id}`).data('url');
    display_active(active_label, active_url);
}

// initialize homepage
const load_homepage = () => {
    // get data elements
    axios.post(fetch_records_url, {
        tablename: 'ContentModel',
        constraints: {
            identifier: 'axa'
        }
    }).then((response) => {
        if (response) {
            // add reference positions to assets
            var assets = response.data.data;
            if (JSON.stringify(assets) == '[]') {
                assets = [{
                    "identifier": "axa",
                    "ord": 0,
                    "label": "Welcome",
                    "url": "docs/welcome.html",
                    "ContentModel_id": "00000000000000000000000000",
                    "__created_at__": 1577983990,
                    "__updated_at__": 1577987875,
                    "__private__": 0,
                    "row_id": 0
                }]
            }
            for (var i = 0; i < assets.length; i++) {
                assets[i]['ref'] = i + assets[i].ord;
            }
            // order by reference positions
            var assets = _.orderBy(assets, 'ref', 'desc');
            // prepare and load nav bar
            $("#navbar").html(generate_navbar(assets));
            // set active assets: active_label, active_url
            display_active(assets[0].label, assets[0].url);
            // update max ref
            $("#myModal").data("maxref", assets[0].ref);
            // hide action buttons
            $(".actions").hide()
        }
    })
}

// adjust asset position
const adjust_asset_position = (asset_id, nudge) => {
    axios.post(fetch_records_url, {
        tablename: 'ContentModel',
        constraints: {
            'ContentModel_id': asset_id
        }
    }).then((response) => {
        var data = response.data.data[0];
        var ord = data.ord + nudge;
        axios.post(update_url, {
            tablename: 'ContentModel',
            constraints: {
                'ContentModel_id': asset_id
            },
            data: {
                'ord': ord
            }
        }).then((response) => {
            // reload page
            window.location.reload()
        });
    });
}

// add new asset
const add_new_asset = (asset_label, asset_url, ord = 0) => {
    // store content model
    axios.post(new_record_url, {
        tablename: 'ContentModel',
        data: {
            identifier: 'axa',
            'ord': ord,
            label: asset_label,
            url: asset_url
        }
    }).then((response) => {
        // reload view
        load_homepage();
    });
}

const postref = (ref, maxref) => {
    $("#myModal").data("curref", ref + 1);
    $("#myModal").data("maxref", maxref);
    $('#myModal').on('shown.bs.modal', () => {
        $('#label-i').focus();
    });
}

// submit form
const submitForm = () => {
    // retrieve data values
    var asset_label = $("#label-i").val();
    var asset_url = $("#url-i").val();
    $("#myModal").hide()
    var curref = $("#myModal").data("curref");
    var maxref = $("#myModal").data("maxref");
    var ord = curref - maxref + 1;
    add_new_asset(asset_label, asset_url, ord);
    window.location.reload()
}

// remove asset
const remove_asset = (asset_id) => {
    axios.post(delete_url, {
        tablename: 'ContentModel',
        constraints: {
            'ContentModel_id': asset_id
        }
    }).then((response) => {
        // reload the page
        window.location.reload()
    });
}