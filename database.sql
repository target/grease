--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;



--
-- Name: grease; Type: SCHEMA; Schema: -;
--

CREATE SCHEMA grease;


SET search_path = grease, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: job_config; Type: TABLE; Schema: grease;
--

CREATE TABLE job_config (
    id integer NOT NULL,
    command_module character varying NOT NULL,
    command_name character varying NOT NULL,
    is_threaded boolean DEFAULT false NOT NULL,
    threads integer DEFAULT 1 NOT NULL,
    human_avg integer DEFAULT 60 NOT NULL,
    machine_avg integer DEFAULT 1 NOT NULL,
    tick integer DEFAULT 1 NOT NULL
);



--
-- Name: job_config_id_seq; Type: SEQUENCE; Schema: grease;
--

CREATE SEQUENCE job_config_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: job_config_id_seq; Type: SEQUENCE OWNED BY; Schema: grease;
--

ALTER SEQUENCE job_config_id_seq OWNED BY job_config.id;


--
-- Name: job_failures; Type: TABLE; Schema: grease;
--

CREATE TABLE job_failures (
    id integer NOT NULL,
    job_id integer NOT NULL,
    failures integer DEFAULT 0 NOT NULL
);



--
-- Name: job_failures_id_seq; Type: SEQUENCE; Schema: grease;
--

CREATE SEQUENCE job_failures_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: job_failures_id_seq; Type: SEQUENCE OWNED BY; Schema: grease;
--

ALTER SEQUENCE job_failures_id_seq OWNED BY job_failures.id;


--
-- Name: job_queue; Type: TABLE; Schema: grease;
--

CREATE TABLE job_queue (
    id integer NOT NULL,
    host_name character varying NOT NULL,
    additional jsonb DEFAULT '[]'::jsonb NOT NULL,
    run_priority integer DEFAULT 10 NOT NULL,
    in_progress boolean DEFAULT false NOT NULL,
    completed boolean DEFAULT false NOT NULL,
    job_id integer NOT NULL,
    request_time timestamp without time zone DEFAULT now() NOT NULL,
    sn_ticket_number character varying,
    sn_link character varying,
    complete_time timestamp without time zone
);



--
-- Name: job_queue_id_seq; Type: SEQUENCE; Schema: grease;
--

CREATE SEQUENCE job_queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: job_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: grease;
--

ALTER SEQUENCE job_queue_id_seq OWNED BY job_queue.id;


--
-- Name: job_servers; Type: TABLE; Schema: grease;
--

CREATE TABLE job_servers (
    id integer NOT NULL,
    host_name character varying NOT NULL,
    execution_environment character varying NOT NULL,
    jobs_assigned integer DEFAULT 0 NOT NULL,
    detector boolean DEFAULT false NOT NULL,
    scheduler boolean DEFAULT false NOT NULL,
    active boolean DEFAULT true NOT NULL,
    activation_time timestamp with time zone DEFAULT now() NOT NULL
);



--
-- Name: job_servers_id_seq; Type: SEQUENCE; Schema: grease;
--

CREATE SEQUENCE job_servers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: job_servers_id_seq; Type: SEQUENCE OWNED BY; Schema: grease;
--

ALTER SEQUENCE job_servers_id_seq OWNED BY job_servers.id;


--
-- Name: job_telemetry; Type: TABLE; Schema: grease;
--

CREATE TABLE job_telemetry (
    id integer NOT NULL,
    command character varying NOT NULL,
    effected integer DEFAULT 0 NOT NULL,
    start_time timestamp without time zone DEFAULT now() NOT NULL,
    entry_time timestamp without time zone DEFAULT now() NOT NULL,
    success boolean DEFAULT false NOT NULL,
    is_daemon boolean DEFAULT false NOT NULL,
    server_id character varying
);



--
-- Name: job_telemetry_daemon; Type: TABLE; Schema: grease;
--

CREATE TABLE job_telemetry_daemon (
    id integer NOT NULL,
    command_id integer NOT NULL,
    class_name character varying NOT NULL,
    execution_success boolean DEFAULT false NOT NULL,
    command_success boolean DEFAULT false NOT NULL,
    effected integer DEFAULT 0 NOT NULL,
    start_time timestamp with time zone,
    server_id character varying NOT NULL,
    reported_to_portal boolean DEFAULT false NOT NULL,
    entry_time timestamp with time zone DEFAULT now()
);



--
-- Name: job_telemetry_daemon_id_seq; Type: SEQUENCE; Schema: grease;
--

CREATE SEQUENCE job_telemetry_daemon_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: job_telemetry_daemon_id_seq; Type: SEQUENCE OWNED BY; Schema: grease;
--

ALTER SEQUENCE job_telemetry_daemon_id_seq OWNED BY job_telemetry_daemon.id;


--
-- Name: job_telemetry_id_seq; Type: SEQUENCE; Schema: grease;
--

CREATE SEQUENCE job_telemetry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: job_telemetry_id_seq; Type: SEQUENCE OWNED BY; Schema: grease;
--

ALTER SEQUENCE job_telemetry_id_seq OWNED BY job_telemetry.id;


--
-- Name: persistant_jobs; Type: TABLE; Schema: grease;
--

CREATE TABLE persistant_jobs (
    id integer NOT NULL,
    host_name character varying NOT NULL,
    additional jsonb DEFAULT '[]'::jsonb NOT NULL,
    job_id integer NOT NULL,
    enabled boolean DEFAULT true NOT NULL
);



--
-- Name: TABLE persistant_jobs; Type: COMMENT; Schema: grease;
--

COMMENT ON TABLE persistant_jobs IS 'jobs to be run every tick';


--
-- Name: persistant_jobs_id_seq; Type: SEQUENCE; Schema: grease;
--

CREATE SEQUENCE persistant_jobs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: persistant_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: grease;
--

ALTER SEQUENCE persistant_jobs_id_seq OWNED BY persistant_jobs.id;


--
-- Name: scheduling_queue; Type: TABLE; Schema: grease;
--

CREATE TABLE scheduling_queue (
    id integer NOT NULL,
    source_data jsonb NOT NULL,
    job_server integer NOT NULL,
    scanner character varying NOT NULL,
    created timestamp with time zone DEFAULT now() NOT NULL,
    in_progress boolean DEFAULT false NOT NULL,
    completed boolean DEFAULT false NOT NULL,
    pick_up_time timestamp with time zone,
    complete_time timestamp with time zone
);



--
-- Name: TABLE scheduling_queue; Type: COMMENT; Schema: grease;
--

COMMENT ON TABLE scheduling_queue IS 'Parsed Source DATA TO GET scheduled';


--
-- Name: scheduling_queue_id_seq; Type: SEQUENCE; Schema: grease;
--

CREATE SEQUENCE scheduling_queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: scheduling_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: grease;
--

ALTER SEQUENCE scheduling_queue_id_seq OWNED BY scheduling_queue.id;


--
-- Name: server_health; Type: TABLE; Schema: grease;
--

CREATE TABLE server_health (
    id integer NOT NULL,
    server_id integer NOT NULL,
    job_hash character varying NOT NULL,
    check_time timestamp with time zone DEFAULT now() NOT NULL,
    doctor character varying
);



--
-- Name: server_health_id_seq; Type: SEQUENCE; Schema: grease;
--

CREATE SEQUENCE server_health_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: server_health_id_seq; Type: SEQUENCE OWNED BY; Schema: grease;
--

ALTER SEQUENCE server_health_id_seq OWNED BY server_health.id;


--
-- Name: source_file; Type: TABLE; Schema: grease;
--

CREATE TABLE source_file (
    id integer NOT NULL,
    source_document jsonb NOT NULL,
    in_progress boolean DEFAULT false NOT NULL,
    completed boolean DEFAULT false NOT NULL,
    job_server integer NOT NULL,
    scanner character varying NOT NULL,
    created timestamp with time zone DEFAULT now() NOT NULL,
    pick_up_time timestamp with time zone,
    completed_time timestamp with time zone
);



--
-- Name: TABLE source_file; Type: COMMENT; Schema: grease;
--

COMMENT ON TABLE source_file IS 'This is where source documents are stored to be processed';


--
-- Name: sources_id_seq; Type: SEQUENCE; Schema: grease;
--

CREATE SEQUENCE sources_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: sources_id_seq; Type: SEQUENCE OWNED BY; Schema: grease;
--

ALTER SEQUENCE sources_id_seq OWNED BY source_file.id;


--
-- Name: job_config id; Type: DEFAULT; Schema: grease;
--

ALTER TABLE ONLY job_config ALTER COLUMN id SET DEFAULT nextval('job_config_id_seq'::regclass);


--
-- Name: job_failures id; Type: DEFAULT; Schema: grease;
--

ALTER TABLE ONLY job_failures ALTER COLUMN id SET DEFAULT nextval('job_failures_id_seq'::regclass);


--
-- Name: job_queue id; Type: DEFAULT; Schema: grease;
--

ALTER TABLE ONLY job_queue ALTER COLUMN id SET DEFAULT nextval('job_queue_id_seq'::regclass);


--
-- Name: job_servers id; Type: DEFAULT; Schema: grease;
--

ALTER TABLE ONLY job_servers ALTER COLUMN id SET DEFAULT nextval('job_servers_id_seq'::regclass);


--
-- Name: job_telemetry id; Type: DEFAULT; Schema: grease;
--

ALTER TABLE ONLY job_telemetry ALTER COLUMN id SET DEFAULT nextval('job_telemetry_id_seq'::regclass);


--
-- Name: job_telemetry_daemon id; Type: DEFAULT; Schema: grease;
--

ALTER TABLE ONLY job_telemetry_daemon ALTER COLUMN id SET DEFAULT nextval('job_telemetry_daemon_id_seq'::regclass);


--
-- Name: persistant_jobs id; Type: DEFAULT; Schema: grease;
--

ALTER TABLE ONLY persistant_jobs ALTER COLUMN id SET DEFAULT nextval('persistant_jobs_id_seq'::regclass);


--
-- Name: scheduling_queue id; Type: DEFAULT; Schema: grease;
--

ALTER TABLE ONLY scheduling_queue ALTER COLUMN id SET DEFAULT nextval('scheduling_queue_id_seq'::regclass);


--
-- Name: server_health id; Type: DEFAULT; Schema: grease;
--

ALTER TABLE ONLY server_health ALTER COLUMN id SET DEFAULT nextval('server_health_id_seq'::regclass);


--
-- Name: source_file id; Type: DEFAULT; Schema: grease;
--

ALTER TABLE ONLY source_file ALTER COLUMN id SET DEFAULT nextval('sources_id_seq'::regclass);


--
-- Name: job_config job_config_pkey; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_config
    ADD CONSTRAINT job_config_pkey PRIMARY KEY (id);


--
-- Name: job_failures job_failures_pkey; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_failures
    ADD CONSTRAINT job_failures_pkey PRIMARY KEY (id);


--
-- Name: job_failures job_id_uq; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_failures
    ADD CONSTRAINT job_id_uq UNIQUE (job_id);


--
-- Name: job_queue job_queue_pkey; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_queue
    ADD CONSTRAINT job_queue_pkey PRIMARY KEY (id);


--
-- Name: job_servers job_servers_pkey; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_servers
    ADD CONSTRAINT job_servers_pkey PRIMARY KEY (id);


--
-- Name: job_telemetry_daemon job_telem_pk; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_telemetry_daemon
    ADD CONSTRAINT job_telem_pk PRIMARY KEY (id);


--
-- Name: job_telemetry job_telemetry_pkey; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_telemetry
    ADD CONSTRAINT job_telemetry_pkey PRIMARY KEY (id);


--
-- Name: persistant_jobs persistant_jobs_pkey; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY persistant_jobs
    ADD CONSTRAINT persistant_jobs_pkey PRIMARY KEY (id);


--
-- Name: scheduling_queue scheduling_queue_pkey; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY scheduling_queue
    ADD CONSTRAINT scheduling_queue_pkey PRIMARY KEY (id);


--
-- Name: server_health server_health_pkey; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY server_health
    ADD CONSTRAINT server_health_pkey PRIMARY KEY (id);


--
-- Name: source_file sources_pkey; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY source_file
    ADD CONSTRAINT sources_pkey PRIMARY KEY (id);


--
-- Name: job_config uq_command_command_name; Type: CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_config
    ADD CONSTRAINT uq_command_command_name UNIQUE (command_name);


--
-- Name: fki_job_config_job_id_fk; Type: INDEX; Schema: grease;
--

CREATE INDEX fki_job_config_job_id_fk ON job_queue USING btree (job_id);


--
-- Name: job_servers_host_name_uindex; Type: INDEX; Schema: grease;
--

CREATE UNIQUE INDEX job_servers_host_name_uindex ON job_servers USING btree (host_name);


--
-- Name: job_servers_id_uindex; Type: INDEX; Schema: grease;
--

CREATE UNIQUE INDEX job_servers_id_uindex ON job_servers USING btree (id);


--
-- Name: persistant_jobs_id_uindex; Type: INDEX; Schema: grease;
--

CREATE UNIQUE INDEX persistant_jobs_id_uindex ON persistant_jobs USING btree (id);


--
-- Name: scheduling_queue_id_uindex; Type: INDEX; Schema: grease;
--

CREATE UNIQUE INDEX scheduling_queue_id_uindex ON scheduling_queue USING btree (id);


--
-- Name: server_health_id_uindex; Type: INDEX; Schema: grease;
--

CREATE UNIQUE INDEX server_health_id_uindex ON server_health USING btree (id);


--
-- Name: sources_id_uindex; Type: INDEX; Schema: grease;
--

CREATE UNIQUE INDEX sources_id_uindex ON source_file USING btree (id);


--
-- Name: job_telemetry_daemon fk_job_config_id_command_id; Type: FK CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_telemetry_daemon
    ADD CONSTRAINT fk_job_config_id_command_id FOREIGN KEY (command_id) REFERENCES job_config(id);


--
-- Name: job_queue job_config_job_id_fk; Type: FK CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_queue
    ADD CONSTRAINT job_config_job_id_fk FOREIGN KEY (job_id) REFERENCES job_config(id);


--
-- Name: job_telemetry job_telemetry_job_servers_host_name_fk; Type: FK CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY job_telemetry
    ADD CONSTRAINT job_telemetry_job_servers_host_name_fk FOREIGN KEY (server_id) REFERENCES job_servers(host_name);


--
-- Name: persistant_jobs persistant_jobs_grease.job_config_id_fk; Type: FK CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY persistant_jobs
    ADD CONSTRAINT "persistant_jobs_grease.job_config_id_fk" FOREIGN KEY (job_id) REFERENCES job_config(id);


--
-- Name: scheduling_queue scheduling_queue_job_servers_id_fk; Type: FK CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY scheduling_queue
    ADD CONSTRAINT scheduling_queue_job_servers_id_fk FOREIGN KEY (job_server) REFERENCES job_servers(id);


--
-- Name: server_health server_health_job_servers_id_fk; Type: FK CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY server_health
    ADD CONSTRAINT server_health_job_servers_id_fk FOREIGN KEY (server_id) REFERENCES job_servers(id);


--
-- Name: source_file source_file_job_servers_id_fk; Type: FK CONSTRAINT; Schema: grease;
--

ALTER TABLE ONLY source_file
    ADD CONSTRAINT source_file_job_servers_id_fk FOREIGN KEY (job_server) REFERENCES job_servers(id);

--
-- Data for Name: job_config; Type: TABLE DATA; Schema: grease;
--

COPY job_config (id, command_module, command_name, is_threaded, threads, human_avg, machine_avg, tick) FROM stdin;
1	enterprise	system_heartbeat	f	1	200	5	50
2	enterprise	engage_warp	f	1	0	1	60
3	enterprise	engage_lcars	f	1	0	0	60
4	enterprise	engage_sensor_array	f	1	0	0	60
\.

--
-- PostgreSQL database dump complete
--