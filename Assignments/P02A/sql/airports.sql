-- Table: public.airports

-- DROP TABLE IF EXISTS public.airports;

CREATE TABLE IF NOT EXISTS public.airports
(
    id numeric NOT NULL,
    name character varying(256) COLLATE pg_catalog."default" NOT NULL,
    city character varying(32) COLLATE pg_catalog."default" NOT NULL,
    country character varying(256) COLLATE pg_catalog."default" NOT NULL,
    three_code character varying(3) COLLATE pg_catalog."default" NOT NULL,
    four_code character varying(4) COLLATE pg_catalog."default" NOT NULL,
    lat numeric(11,8) NOT NULL,
    lon numeric(11,8) NOT NULL,
    elevation character varying(10) COLLATE pg_catalog."default",
    gmt character varying(10) COLLATE pg_catalog."default",
    tz_short character varying(2) COLLATE pg_catalog."default",
    time_zone character varying(32) COLLATE pg_catalog."default",
    type character varying(32) COLLATE pg_catalog."default",
    location geometry(Point,4326),
    CONSTRAINT airports_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.airports
    OWNER to postgres;
-- Index: airports_geom_idx

-- DROP INDEX IF EXISTS public.airports_geom_idx;

CREATE INDEX IF NOT EXISTS airports_geom_idx
    ON public.airports USING gist
    (location)
    TABLESPACE pg_default;