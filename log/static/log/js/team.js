/*------------------------------------------------------------------------
{   Loading table packages; drawing table once loaded
------------------------------------------------------------------------*/
google.charts.load('current', {'packages':['table']});
google.charts.setOnLoadCallback(drawTable);

/*------------------------------------------------------------------------
Create DataTable, then pluggin DataTable into Table object
------------------------------------------------------------------------*/
function drawTable() {
    var data = new google.visualization.DataTable();

    /*--------------------------------------------------------------------
    Adding columns, then providing rows for these columns
    --------------------------------------------------------------------*/
    data.addColumn('string', 'First');
    data.addColumn('string', 'Last');
    data.addColumn('string', 'Grade');
    data.addColumn('number', 'Rank');
    data.addRows(athleteData);

    /*--------------------------------------------------------------------
    Creating table, but not drawing yet
    --------------------------------------------------------------------*/  
    var table = new google.visualization.Table(document.getElementById('athletes'));

    /*--------------------------------------------------------------------
    Adding a 'ready' event listener - this way we know the table has 
    loaded before attempting any interactions with it
    --------------------------------------------------------------------*/
    google.visualization.events.addListener(table, 'ready', myReadyHandler);
    google.visualization.events.addListener(table, 'sort', handleSort);

    /*--------------------------------------------------------------------
    Need to reapply hover and clickability of rows
    --------------------------------------------------------------------*/
    function handleSort(e) {
        myReadyHandler();
    }

    /*--------------------------------------------------------------------
    Called once table has loaded
    --------------------------------------------------------------------*/
    function myReadyHandler() {
        sortIndices = table.getSortInfo().sortedIndexes
        
        /*----------------------------------------------------------------
        IF the table has been sorted, we now have a list of <tr> indices
        ----------------------------------------------------------------*/
        if (sortIndices){
            /*----------------------------------------------------------------
            Add id's to all but first row (column names)
            ----------------------------------------------------------------*/
            $("tr.athlete").each(function(index) {
                $(this).attr('id', userIDs[sortIndices[index]]);
                $(this).attr('class', 'athlete');
            });
        }

        /*----------------------------------------------------------------
        ELSE, sortIndices is NULL and we can just index in order
        ----------------------------------------------------------------*/
        else {
            $("tr").not(':first').each(function(index) {
                $(this).attr('id', userIDs[index]);  
                $(this).attr('class', 'athlete');
                console.log($(this));
            });
        }

        /*----------------------------------------------------------------
        On hover, suggest clickability
        ----------------------------------------------------------------*/
        $("tr.athlete").hover(function() {
            console.log('here');
            $(this).css({"cursor": "pointer"});
        });

        /*----------------------------------------------------------------
        On click, redirect to selected athlete's page
        ----------------------------------------------------------------*/
        $("tr.athlete").click(function() {
            window.location.href = "/log/athlete/"+$(this).attr('id');
        });
    }
    
    var cssClassNames = {'headerRow': 'italic-darkblue-font large-font bold-font'};

    /*--------------------------------------------------------------------
    Draw the table using the DataTable we created earlier
    --------------------------------------------------------------------*/
    table.draw(data, {'showRowNumber': true, 'width': '100%', 'cssClassNames': cssClassNames});     
} 


google.charts.setOnLoadCallback(drawTable2);
/*------------------------------------------------------------------------
Create DataTable, then pluggin DataTable into Table object
------------------------------------------------------------------------*/
function drawTable2() {
    var data = new google.visualization.DataTable();

    /*--------------------------------------------------------------------
    Adding columns, then providing rows for these columns
    --------------------------------------------------------------------*/
    data.addColumn('string', 'Location');
    data.addColumn('string', 'Date');
    data.addColumn('number', 'Distance');
    data.addColumn('number', 'Rank');
    data.addRows(meetData);

    /*--------------------------------------------------------------------
    Creating table, but not drawing yet
    --------------------------------------------------------------------*/  
    var table = new google.visualization.Table(document.getElementById('meets'));

    /*--------------------------------------------------------------------
    Draw the table using the DataTable we created earlier
    --------------------------------------------------------------------*/
    table.draw(data, {showRowNumber: true, width: '100%'});     
} 