-- Table: public.military_bases

-- DROP TABLE IF EXISTS public.military_bases;

CREATE TABLE IF NOT EXISTS public.military_bases
(
    gid integer NOT NULL DEFAULT nextval('military_bases_gid_seq'::regclass),
    ansicode character varying(8) COLLATE pg_catalog."default",
    areaid character varying(22) COLLATE pg_catalog."default",
    fullname character varying(100) COLLATE pg_catalog."default",
    mtfcc character varying(5) COLLATE pg_catalog."default",
    aland double precision,
    awater double precision,
    intptlat character varying(11) COLLATE pg_catalog."default",
    intptlon character varying(12) COLLATE pg_catalog."default",
    CONSTRAINT military_bases_pkey PRIMARY KEY (gid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.military_bases
    OWNER to postgres;