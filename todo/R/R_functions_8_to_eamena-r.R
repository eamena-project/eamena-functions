# miscellaneous of R functions

library(hash)
library(geojsonio)
library(dplyr)
library(igraph)
library(stringr)
library(tidyr)
library(ggplot2)
library(plotly)
library(leaflet)
library(htmlwidgets)
library(sf)

raw.GH <- "https://raw.githubusercontent.com/eamena-oxford/eamena-arches-dev/main/"
time.results <-  paste0(getwd(), "/data/time/results/")


#' Basic statistic on EAMENA heritage places
#' @name basic_stats
#' @description Count the number of HP, ...
#'
#' @param db the name of the database, by default 'eamena'
#' @param d a hash() object (a Python-like dictionary)
#' @param field the name of the field that will be created in the a hash() object.
#' By default 'count_hp' (see 'stat.choice' and 'rm.choice' parameters)
#' @param stat.choice the type of statistics ('count', 'duplicates', etc.)
#' @param rm.choice the type of resources on which this statistics will be
#' applied (eg: 'hp' for Heritage Places)
#' @return Basic statistics
#'
#' @examples
#'
#' # By default count the total number of Heritage Places
#' d_sql <- hash::hash()
#' d_sql <- count_hps(con, d_sql)
#'
#' @export
basic_stats <- function(db, d, field = "count_hp", stat.choice = "count", rm.choice = "hp"){
  if(stat.choice == "count" & rm.choice == "hp"){
    # count Heritage Places (HPs)
    sqll <- "
    SELECT
    count(tiledata->>'34cfe992-c2c0-11ea-9026-02e7594ce0a0' like '%EAMENA%') as HPs_count
    FROM tiles;
    "
  }
  if(stat.choice == "duplicates" & rm.choice == "hp"){
    sqll <- "
    SELECT
    tiledata->>'34cfe992-c2c0-11ea-9026-02e7594ce0a0'::text as EAMENAID,
    count(*) AS count
    FROM tiles
    GROUP BY EAMENAID
    HAVING count(*) > 1
    ORDER BY EAMENAID;
    "
  }
  con <- my_con(db) # load the Pg connection
  d[[field]] <- dbGetQuery(con, sqll)
  dbDisconnect(con)
  return(d)
}

#' The threats on HP
#' @name threats_hps
#' @description Read the DB and gather the different threats by HP. A join with the table 'values'
#' is needed since the 'tiles' table gathers principally UUID that must be translated
#' into human-readable values. Collect fields: EAMENA_ID, ThreatCat, AssessType,
#' AssessDate, resourceinstanceid
#'
#' @param db a Pg connection
#' @param d a hash() object (a Python-like dictionary)
#' @param field the name of the field that will be created in the a hash() object
#' @return A hash() with all threats, dates, etc. stored in the field name
#'
#' @examples
#'
#' @export
threats_hps <- function(db, d, field){
  sqll <- "
  SELECT
  tiles.tiledata ->> '34cfe992-c2c0-11ea-9026-02e7594ce0a0' as EamenaID,
  values1.value as ThreatCat,
  values2.value as ActivTyp,
  tiles.tiledata ->> '34cfea81-c2c0-11ea-9026-02e7594ce0a0' as AssessDat,
  resourceinstanceid as ResourceID
  FROM tiles
  LEFT JOIN values as values1 ON
  values1.valueid::text = tiledata ->> '34cfea76-c2c0-11ea-9026-02e7594ce0a0'
  LEFT JOIN values as values2 ON
  values2.valueid::text = tiledata ->> '34cfea4d-c2c0-11ea-9026-02e7594ce0a0'
  WHERE ((nodegroupid::text = '34cfea2e-c2c0-11ea-9026-02e7594ce0a0')
		 OR (nodegroupid::text = '34cfe9fb-c2c0-11ea-9026-02e7594ce0a0')
		 OR (nodegroupid::text = '34cfe992-c2c0-11ea-9026-02e7594ce0a0')
		 OR (nodegroupid::text = '34cfea4d-c2c0-11ea-9026-02e7594ce0a0')
		)
  ORDER BY resourceid
  -- LIMIT 5000
  "
  con <- my_con(db) # load the Pg connection
  d[[field]] <- dbGetQuery(con, sqll)
  dbDisconnect(con)
  return(d)
}





#' #' Return the UUID of a HP from EAMENA id
#' #' @name uuid_from_eamenaid
#' #' @description Return the UUID of a HP from EAMENA id and store it into a hash() object
#' #' alongside the EAMENA id
#' #'
#' #' @param db the name of the database, by default 'eamena'
#' #' @param d a hash() object (a Python-like dictionary)
#' #' @param eamenaid a EAMENA ID (eg. "EAMENA-0187363")
#' #' @param field.uuid the name of the field that will be created in the a hash() object
#' #' for the UUID
#' #' @param field.eamenaid the name of the field that will be created in the a hash() object
#' #' for the EAMENA ID
#' #' @return a hash() object (a Python-like dictionary) with EAMENA ID and UUID
#' #'
#' #' @examples
#' #' d_sql <- hash::hash() # hash instance to store the results
#' #' d_sql <- uuid_from_eamenaid("eamena", d_sql, "EAMENA-0187363")
#' #'
#' #' @export
#' uuid_from_eamenaid <- function(db, d, eamenaid, field.uuid = "uuid", field.eamenaid = "eamenaid"){
#'   # eamenaid <-  c("EAMENA-0187363", "EAMENA-0184752", "EAMENA-0076769")
#'   if(length(eamenaid) == 1){
#'     sqll <- str_interp("
#'     SELECT
#'     resourceinstanceid
#'     FROM tiles
#'     WHERE tiledata ->> '34cfe992-c2c0-11ea-9026-02e7594ce0a0'::text LIKE '%${eamenaid}%'
#'                        ")
#'     # sqll <- str_interp("
#'     # SELECT t.tileid, t.resourceinstanceid, t.tiledata, n.nodeid
#'     # FROM tiles t LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
#'     # WHERE (t.tiledata::json -> n.nodeid::text)::text LIKE '%${eamenaid}%'
#'     #                    ")
#'   }
#'   if(length(eamenaid) > 1){
#'     # TODO: does it work for only 1 UUID?
#'     eamenaids <- paste0(eamenaid, collapse = "|")
#'     sqll <- str_interp("
#'     SELECT
#'     resourceinstanceid
#'     FROM tiles
#'     WHERE tiledata ->> '34cfe992-c2c0-11ea-9026-02e7594ce0a0'::text SIMILAR to '%(${eamenaids})%'
#'                        ")
#'     # sqll <- str_interp("
#'     # SELECT
#'     # t.tileid, t.resourceinstanceid, t.tiledata, n.nodeid
#'     # FROM tiles t LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
#'     # WHERE (t.tiledata::json -> n.nodeid::text)::text SIMILAR to '%(${eamenaids})%'
#'     # ")
#'     # print(sqll)
#'   }
#'   con <- my_con(db) # load the Pg connection
#'   df <- dbGetQuery(con, sqll)
#'   d[[field.eamenaid]] <- eamenaid
#'   d[[field.uuid]] <- as.character(df$resourceinstanceid)
#'   dbDisconnect(con)
#'   return(d)
#' }


#' List the name of all the cultural period of a given HP
#' @name list_culturalper
#' @description With a given concept UUID (v. Reference Data Manager), find all
#' the cultural periods, subperiods, etc., of a given HP
#'
#' @param db the name of the database or dataset, by default 'eamena'. If 'eamena'
#' will connect the Pg database. If 'geojson', will read the GeoJSON file path
#' recorded in the parameter 'geojson.path'
#' @param d a hash() object (a Python-like dictionary)
#' @param field the field name that will be created in the a hash() object
#' @param uuid the UUID of the HP, only useful if db = 'eamena'
#' @param geojson.path the path of the GeoJSON file
#'
#' @return A hash() with listed cultural periods names
#'
#' @examples
#'
#' d_sql <- hash::hash()
#' d_sql <- uuid_from_eamenaid("eamena", "EAMENA-0187363", d_sql, "uuid")
#' d_sql <- list_culturalper("eamena", d_sql, "culturalper", d_sql$uuid)
#'
#' @export
list_culturalper <- function(db = 'eamena', d, field, uuid = NA, geojson.path = NA){
  # TODO: field is useful?
  # d <- d_sql ; uuid <- '12053a2b-9127-47a4-990f-7f5279cd89da'; field <- "culturalper"
  # d <- d_sql ; uuid <- d_sql[["uuid"]]; field <- "culturalper"
  # d <- d_sql ; uuid <- d_sql[["uuid"]]; field <- "culturalper" ; db = 'geojson' ; geojson.path = 'https://raw.githubusercontent.com/eamena-oxford/eamena-arches-dev/main/data/geojson/caravanserail.geojson'
  df.periods.template <- data.frame(eamenaid = character(0),
                                    periods = character(0),
                                    periods.certain = character(0),
                                    name.periods = character(0),
                                    name.periods.certain = character(0)
  )
  df.subperiods.template <- data.frame(eamenaid = character(0),
                                       subperiods = character(0),
                                       subperiods.certain = character(0),
                                       name.subperiods = character(0),
                                       name.subperiods.certain = character(0)
  )
  #length(uuid)
  if(db == "eamena"){
    for (i in seq(1, length(uuid))){
      # i <- 2
      # print(i)
      if(i %% 10 == 0){print(paste("*read:", i, "/", length(uuid)))}
      a.uuid <- uuid[i]
      a.eamenaid <- d$eamenaid[i]
      sqll <- str_interp("
      SELECT
      '${a.eamenaid}' AS eamenaid,
      tiledata ->> '38cff73b-c77b-11ea-a292-02e7594ce0a0' AS periods,
      tiledata ->> '38cff738-c77b-11ea-a292-02e7594ce0a0' AS periods_certain,
      tiledata ->> '38cff73c-c77b-11ea-a292-02e7594ce0a0' AS subperiods,
      tiledata ->> '38cff73a-c77b-11ea-a292-02e7594ce0a0' AS subperiods_certain
      FROM tiles
      WHERE resourceinstanceid = '${a.uuid}'
                     ")
      con <- my_con(db) # load the Pg connection
      df.part <- dbGetQuery(con, sqll)
    }
  }
  if(db == "geojson"){
    eamenaid <- geojson_get_field(geojson.path, "EAMENA.ID")
    periods <- geojson_get_field(geojson.path, "Cultural.Period.Type")
    periods_certain <- geojson_get_field(geojson.path, "Cultural.Period.Certainty")
    subperiods <- geojson_get_field(geojson.path, "Cultural.Sub.period.Type")
    subperiods_certain <- geojson_get_field(geojson.path, "Cultural.Sub.period.Certainty")
    df.part <- data.frame(eamenaid = eamenaid,
                          periods = periods,
                          periods_certain = periods_certain,
                          subperiods = subperiods,
                          subperiods_certain = subperiods_certain)
  }
  # con <- my_con(db) # load the Pg connection
  # df <- dbGetQuery(con, sqll)
  # dbDisconnect(con)
  periods <- df.part[!(is.na(df.part$periods) | df.part$periods == ""), ]
  if(nrow(periods) > 0){
    # df.periods <- data.frame(eamenaid = periods$eamenaid,
    #                          periods = periods$periods,
    #                          periods.certain = periods$periods_certain,
    #                          name.periods = rep(NA, nrow(periods)),
    #                          name.periods.certain = rep(NA, nrow(periods))
    # )
    df.periods <- data.frame(eamenaid = periods$eamenaid,
                             periods = periods$periods,
                             periods.certain = periods$periods_certain
    )
    cultural_periods <- read.table(paste0(raw.GH, "data/time/results/cultural_periods.tsv"),
                                   sep = "\t", header = T)
    df.periods.template <- merge(df.periods, cultural_periods, by.x = "periods", by.y = "ea.name", all.x = TRUE)
    # df.periods <- name_from_uuid(db = db, df = df.periods,
    #                              uuid.in = "periods", field.out = "name.periods")
    # df.periods <- name_from_uuid(db = db, df = df.periods,
    #                              uuid.in = "periods.certain", field.out = "name.periods.certain")
    # df.periods.template <- rbind(df.periods.template, df.periods)
  }
  subperiods <- df.part[!(is.na(df.part$subperiods) | df.part$subperiods == ""), ]
  if(nrow(subperiods) > 0){
    df.subperiods <- data.frame(eamenaid = subperiods$eamenaid,
                                subperiods = subperiods$subperiods,
                                subperiods.certain = subperiods$subperiods_certain
    )
    # df.subperiods <- data.frame(eamenaid = subperiods$eamenaid,
    #                             subperiods = subperiods$subperiods,
    #                             subperiods.certain = subperiods$subperiods_certain,
    #                             name.subperiods = rep(NA, nrow(subperiods)),
    #                             name.subperiods.certain = rep(NA, nrow(subperiods))
    # )
    # df.subperiods <- name_from_uuid(db = db, df = df.subperiods,
    #                                 uuid.in = "subperiods", field.out = "name.subperiods")
    # df.subperiods <- name_from_uuid(db = db, df = df.subperiods,
    #                                 uuid.in = "subperiods.certain", field.out = "name.subperiods.certain")
    # df.subperiods.template <- rbind(df.subperiods.template, df.subperiods)
    cultural_periods <- read.table(paste0(raw.GH, "data/time/results/cultural_periods.tsv"),
                                   sep = "\t", header = T)
    df.subperiods.template <- merge(df.subperiods, cultural_periods, by.x = "subperiods", by.y = "ea.name", all.x = TRUE)
  }
  # clean
  df.periods.template <- df.periods.template[df.periods.template$eamenaid != "NA", ]
  df.periods.template <- df.periods.template[df.periods.template$periods != "Unknown", ]

  df.subperiods.template <- df.subperiods.template[df.subperiods.template$eamenaid != "NA", ]
  df.subperiods.template <- df.subperiods.template[df.subperiods.template$subperiods != "Unknown", ]

  # store in tibble
  ifelse(nrow(df.periods.template) > 0, periods.out <- df.periods.template, periods.out <- NA)
  ifelse(nrow(df.subperiods.template) > 0, subperiods.out <- df.subperiods.template, subperiods.out <- NA)

  dbDisconnect(con)
  df.tibble <- tibble(
    period = periods.out,
    # subperiods = subperiods.out
  )
  d[["period"]] <- tibble(period = periods.out)# subperiods = subperiods.out
  d[["subperiod"]] <- tibble(subperiod = subperiods.out)# subperiods = subperiods.out
  return(d)
}

#' Get the name (eg, of Cultural Periods) from their UUID
#' @name name_from_uuid
#' @description This function is run by list_culturalper()
#'
#' @param db the name of the database, by default 'eamena'
#' @param df a dataframe with at least a colum 'uuid'
#' @param uuid.in the UUID column to read, by default 'uuid'
#' @param field the name of the dataframe field that will be filled with names
#'
#' @return a dataframe with the UUID and the name (eg, of Cultural Periods)
#'
#' @examples
#'
#' @export
name_from_uuid <- function(db = "eamena", df, uuid.in = "uuid", field.out = "name"){
  # uuid = "periods" ; df = df.periods ; field = "name.periods"
  con <- my_con(db) # load the Pg connection
  for(i in seq(1, nrow(df))){
    # i <- 1
    uuid_ <- df[i, uuid.in]
    sqll <- str_interp("
    SELECT value FROM values WHERE valueid = '${uuid_}'
                     ")
    name <- dbGetQuery(con, sqll)
    name <- as.character(name)
    df[i, field.out] <- name
  }
  dbDisconnect(con)
  return(df)
}





#' Create an interactive tree for a given Concept and its concepts-child
#' (eg: 'Cultural Period')
#' @name tree_concepts
#' @description Read the arborescence of concept below of a given concept,
#' creates a collapsibleTree. Plot it by defaut, but if 'export.tree' will
#' export it
#'
#' @param db the name of the database, by default 'eamena'
#' @param d a hash() object (a Python-like dictionary)
#' @param field the field name that will be created in the a hash() object and
#' the name of the collapsibleTree if exported
#' @param export.tree if True, export the tree as a HTML widget

#' @return a plot or a HTML widget of the tree
#'
#' @examples
#'
#' @export
tree_concepts <- function(db = "eamena", d, field, export.tree = F){
  # TODO: put UUID in the function options
  d <- list_cpts(db, d, field, '3b5c9ac7-5615-3de6-9e2d-4cd7ef7460e4')
  g <- d[[field]]
  leaves <- V(g)[degree(g, mode="out") == 0]
  leaves <- leaves$name # all the periods (and superiods?)
  # format for collapsibleTree
  edges.cultural.period <- as_data_frame(g, what = "edges")
  edges.cultural.period$root <- "cultural.period"
  edges.cultural.period <- edges.cultural.period[edges.cultural.period$from != "Cultural Period", ]
  tree.edges.cultural.period <- collapsibleTree(edges.cultural.period,
                                                hierarchy = c("root", "from", "to"),
                                                root = "Thesauri",
                                                c("from", "to"),
                                                collapsed = FALSE,
                                                width = 1200,
                                                height = 900)
  if(export.tree){
    saveWidget(as_widget(tree.edges.cultural.period),
               paste0(getwd(),"/data/time/results/",
                      filed.out, ".html"))
  } else {
    # plot
    tree.edges.cultural.period
  }
}

#' #' Get a list of parameters from a GeoJSON file.
#' #' @name geojson_get_field
#' #' @description Get values of a given field
#' #'
#' #' @param geojson.path the path to the GeoJSON file,
#' #' eg: "https://raw.githubusercontent.com/eamena-oxford/eamena-arches-dev/main/data/geojson/caravanserail.geojson"
#' #' @param field a field name, in R format, eg: EAMENA.ID
#' #'
#' #' @return A vector with all values
#' #'
#' #' @examples
#' #'
#' #' @export
#' geojson_get_field <- function(geojson.path, field = "EAMENA.ID"){
#'   # geojson.path <- "https://raw.githubusercontent.com/eamena-oxford/eamena-arches-dev/main/data/geojson/caravanserail.geojson"
#'   # field = "Cultural.Sub.period.Type"
#'   r <- geojson_read(geojson.path)
#'   all.val <- c()
#'   for(i in seq(1, length(r[[2]]))){
#'     # print(i)
#'     val <- r[[2]][[i]]$properties[[field]]
#'     # print(val)
#'     # print(is.null(val))
#'     if(is.null(val)){val <- NA}
#'     all.val <- c(all.val, val)
#'   }
#'   return(all.val)
#' }





