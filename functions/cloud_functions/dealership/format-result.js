function main(params) {
    //return params
  if (!params.result) {
     return {
        statusCode: 500,
        message: "Something went wrong on the server"
     };  

  }
if (params.result.length==0) {
    const empty_message=(params.state) ? "The state does not exist" : "The database is empty"
    return ({
        statusCode: 400,
        message: empty_message
      });  
  }
  return {
    entries: params.result.map((row) => { 
        if (row.doc) {
            return {
              id: row.doc.id,
              city: row.doc.city,
              state: row.doc.state,
              st: row.doc.st,
              address: row.doc.address,
              zip: row.doc.zip,
              lat: row.doc.lat,   
              long: row.doc.long,
              full_name:row.doc.full_name,
              short_name:row.doc.short_name,
            }
        } else if (row.id) {
            return {
              id: row.id,
              city: row.city,
              state: row.state,
              st: row.st,
              address: row.address,
              zip: row.zip,
              lat: row.lat,   
              long: row.long,   
              full_name:row.full_name,
              short_name:row.short_name,
            } 
        } else {
            return params
        }
    })
  };
  
}