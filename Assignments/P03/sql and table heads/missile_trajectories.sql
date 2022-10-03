-- Table: public.missile_trajectories

-- DROP TABLE IF EXISTS public.missile_trajectories;

CREATE TABLE IF NOT EXISTS public.missile_trajectories
(
    id numeric NOT NULL,
    altitude numeric NOT NULL,
    speed numeric NOT NULL,
    degree numeric(11,8) NOT NULL,
    start_longitude numeric(11,8) NOT NULL,
    start_latitude numeric(11,8) NOT NULL,
    end_longitude numeric(11,8) NOT NULL,
    end_latitude numeric(11,8) NOT NULL,
    geom geometry,
    CONSTRAINT missile_trajectories_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.missile_trajectories
    OWNER to postgres;
-- Index: missile_paths_geom_idx

-- DROP INDEX IF EXISTS public.missile_paths_geom_idx;

CREATE INDEX IF NOT EXISTS missile_paths_geom_idx
    ON public.missile_trajectories USING gist
    (geom)
    TABLESPACE pg_default;