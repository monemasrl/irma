--
-- PostgreSQL database dump
--

-- Dumped from database version 14.4 (Debian 14.4-1.pgdg110+1)
-- Dumped by pg_dump version 14.4 (Debian 14.4-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

\connect chirpstack_ns

--
-- Name: code_migration; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.code_migration (
    id text NOT NULL,
    applied_at timestamp with time zone NOT NULL
);


ALTER TABLE public.code_migration OWNER TO chirpstack_ns;

--
-- Name: device; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.device (
    dev_eui bytea NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    device_profile_id uuid NOT NULL,
    service_profile_id uuid NOT NULL,
    routing_profile_id uuid NOT NULL,
    skip_fcnt_check boolean DEFAULT false NOT NULL,
    reference_altitude double precision NOT NULL,
    mode character(1) NOT NULL,
    is_disabled boolean NOT NULL
);


ALTER TABLE public.device OWNER TO chirpstack_ns;

--
-- Name: device_activation; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.device_activation (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    dev_eui bytea NOT NULL,
    join_eui bytea NOT NULL,
    dev_addr bytea NOT NULL,
    f_nwk_s_int_key bytea NOT NULL,
    s_nwk_s_int_key bytea NOT NULL,
    nwk_s_enc_key bytea NOT NULL,
    dev_nonce integer NOT NULL,
    join_req_type smallint NOT NULL
);


ALTER TABLE public.device_activation OWNER TO chirpstack_ns;

--
-- Name: device_activation_id_seq; Type: SEQUENCE; Schema: public; Owner: chirpstack_ns
--

CREATE SEQUENCE public.device_activation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_activation_id_seq OWNER TO chirpstack_ns;

--
-- Name: device_activation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: chirpstack_ns
--

ALTER SEQUENCE public.device_activation_id_seq OWNED BY public.device_activation.id;


--
-- Name: device_multicast_group; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.device_multicast_group (
    dev_eui bytea NOT NULL,
    multicast_group_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.device_multicast_group OWNER TO chirpstack_ns;

--
-- Name: device_profile; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.device_profile (
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    device_profile_id uuid NOT NULL,
    supports_class_b boolean NOT NULL,
    class_b_timeout integer NOT NULL,
    ping_slot_period integer NOT NULL,
    ping_slot_dr integer NOT NULL,
    ping_slot_freq bigint NOT NULL,
    supports_class_c boolean NOT NULL,
    class_c_timeout integer NOT NULL,
    mac_version character varying(10) NOT NULL,
    reg_params_revision character varying(20) NOT NULL,
    rx_delay_1 integer NOT NULL,
    rx_dr_offset_1 integer NOT NULL,
    rx_data_rate_2 integer NOT NULL,
    rx_freq_2 bigint NOT NULL,
    factory_preset_freqs bigint[],
    max_eirp integer NOT NULL,
    max_duty_cycle integer NOT NULL,
    supports_join boolean NOT NULL,
    rf_region character varying(20) NOT NULL,
    supports_32bit_fcnt boolean NOT NULL,
    adr_algorithm_id character varying(100) NOT NULL
);


ALTER TABLE public.device_profile OWNER TO chirpstack_ns;

--
-- Name: device_queue; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.device_queue (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    dev_eui bytea,
    frm_payload bytea,
    f_cnt integer NOT NULL,
    f_port integer NOT NULL,
    confirmed boolean NOT NULL,
    is_pending boolean NOT NULL,
    timeout_after timestamp with time zone,
    emit_at_time_since_gps_epoch bigint,
    dev_addr bytea,
    retry_after timestamp with time zone
);


ALTER TABLE public.device_queue OWNER TO chirpstack_ns;

--
-- Name: device_queue_id_seq; Type: SEQUENCE; Schema: public; Owner: chirpstack_ns
--

CREATE SEQUENCE public.device_queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_queue_id_seq OWNER TO chirpstack_ns;

--
-- Name: device_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: chirpstack_ns
--

ALTER SEQUENCE public.device_queue_id_seq OWNED BY public.device_queue.id;


--
-- Name: gateway; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.gateway (
    gateway_id bytea NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    first_seen_at timestamp with time zone,
    last_seen_at timestamp with time zone,
    location point NOT NULL,
    altitude double precision NOT NULL,
    gateway_profile_id uuid,
    routing_profile_id uuid NOT NULL,
    tls_cert bytea,
    service_profile_id uuid
);


ALTER TABLE public.gateway OWNER TO chirpstack_ns;

--
-- Name: gateway_board; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.gateway_board (
    id smallint NOT NULL,
    gateway_id bytea NOT NULL,
    fpga_id bytea,
    fine_timestamp_key bytea
);


ALTER TABLE public.gateway_board OWNER TO chirpstack_ns;

--
-- Name: gateway_profile; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.gateway_profile (
    gateway_profile_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    channels smallint[] NOT NULL,
    stats_interval bigint NOT NULL
);


ALTER TABLE public.gateway_profile OWNER TO chirpstack_ns;

--
-- Name: gateway_profile_extra_channel; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.gateway_profile_extra_channel (
    id bigint NOT NULL,
    gateway_profile_id uuid NOT NULL,
    modulation character varying(10) NOT NULL,
    frequency integer NOT NULL,
    bandwidth integer NOT NULL,
    bitrate integer NOT NULL,
    spreading_factors smallint[]
);


ALTER TABLE public.gateway_profile_extra_channel OWNER TO chirpstack_ns;

--
-- Name: gateway_profile_extra_channel_id_seq; Type: SEQUENCE; Schema: public; Owner: chirpstack_ns
--

CREATE SEQUENCE public.gateway_profile_extra_channel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gateway_profile_extra_channel_id_seq OWNER TO chirpstack_ns;

--
-- Name: gateway_profile_extra_channel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: chirpstack_ns
--

ALTER SEQUENCE public.gateway_profile_extra_channel_id_seq OWNED BY public.gateway_profile_extra_channel.id;


--
-- Name: multicast_group; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.multicast_group (
    id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    mc_addr bytea,
    mc_nwk_s_key bytea,
    f_cnt integer NOT NULL,
    group_type character(1) NOT NULL,
    dr integer NOT NULL,
    frequency bigint NOT NULL,
    ping_slot_period integer NOT NULL,
    routing_profile_id uuid NOT NULL,
    service_profile_id uuid NOT NULL
);


ALTER TABLE public.multicast_group OWNER TO chirpstack_ns;

--
-- Name: multicast_queue; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.multicast_queue (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    schedule_at timestamp with time zone NOT NULL,
    emit_at_time_since_gps_epoch bigint,
    multicast_group_id uuid NOT NULL,
    gateway_id bytea NOT NULL,
    f_cnt integer NOT NULL,
    f_port integer NOT NULL,
    frm_payload bytea,
    updated_at timestamp with time zone NOT NULL,
    retry_after timestamp with time zone
);


ALTER TABLE public.multicast_queue OWNER TO chirpstack_ns;

--
-- Name: multicast_queue_id_seq; Type: SEQUENCE; Schema: public; Owner: chirpstack_ns
--

CREATE SEQUENCE public.multicast_queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.multicast_queue_id_seq OWNER TO chirpstack_ns;

--
-- Name: multicast_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: chirpstack_ns
--

ALTER SEQUENCE public.multicast_queue_id_seq OWNED BY public.multicast_queue.id;


--
-- Name: routing_profile; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.routing_profile (
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    routing_profile_id uuid NOT NULL,
    as_id character varying(255),
    ca_cert text DEFAULT ''::text NOT NULL,
    tls_cert text DEFAULT ''::text NOT NULL,
    tls_key text DEFAULT ''::text NOT NULL
);


ALTER TABLE public.routing_profile OWNER TO chirpstack_ns;

--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.schema_migrations (
    version bigint NOT NULL,
    dirty boolean NOT NULL
);


ALTER TABLE public.schema_migrations OWNER TO chirpstack_ns;

--
-- Name: service_profile; Type: TABLE; Schema: public; Owner: chirpstack_ns
--

CREATE TABLE public.service_profile (
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    service_profile_id uuid NOT NULL,
    ul_rate integer NOT NULL,
    ul_bucket_size integer NOT NULL,
    ul_rate_policy character(4) NOT NULL,
    dl_rate integer NOT NULL,
    dl_bucket_size integer NOT NULL,
    dl_rate_policy character(4) NOT NULL,
    add_gw_metadata boolean NOT NULL,
    dev_status_req_freq integer NOT NULL,
    report_dev_status_battery boolean NOT NULL,
    report_dev_status_margin boolean NOT NULL,
    dr_min integer NOT NULL,
    dr_max integer NOT NULL,
    channel_mask bytea,
    pr_allowed boolean NOT NULL,
    hr_allowed boolean NOT NULL,
    ra_allowed boolean NOT NULL,
    nwk_geo_loc boolean NOT NULL,
    target_per integer NOT NULL,
    min_gw_diversity integer NOT NULL,
    gws_private boolean DEFAULT false NOT NULL
);


ALTER TABLE public.service_profile OWNER TO chirpstack_ns;

--
-- Name: device_activation id; Type: DEFAULT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device_activation ALTER COLUMN id SET DEFAULT nextval('public.device_activation_id_seq'::regclass);


--
-- Name: device_queue id; Type: DEFAULT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device_queue ALTER COLUMN id SET DEFAULT nextval('public.device_queue_id_seq'::regclass);


--
-- Name: gateway_profile_extra_channel id; Type: DEFAULT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.gateway_profile_extra_channel ALTER COLUMN id SET DEFAULT nextval('public.gateway_profile_extra_channel_id_seq'::regclass);


--
-- Name: multicast_queue id; Type: DEFAULT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.multicast_queue ALTER COLUMN id SET DEFAULT nextval('public.multicast_queue_id_seq'::regclass);


--
-- Data for Name: code_migration; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.code_migration (id, applied_at) FROM stdin;
migrate_to_cluster_keys	2022-07-08 09:37:02.752749+00
migrate_to_golang_migrate	2022-07-08 09:37:03.177838+00
\.


--
-- Data for Name: device; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.device (dev_eui, created_at, updated_at, device_profile_id, service_profile_id, routing_profile_id, skip_fcnt_check, reference_altitude, mode, is_disabled) FROM stdin;
\\x2232330000888802	2022-07-07 15:24:34.937387+00	2022-07-12 10:11:32.376811+00	be018f1b-c068-43c0-a276-a7665ff090b4	80ad5686-bc53-485a-8cd1-c342b5f087dc	6d5db27e-4ce2-4b2b-b5d7-91f069397978	t	0	C	f
\.


--
-- Data for Name: device_activation; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.device_activation (id, created_at, dev_eui, join_eui, dev_addr, f_nwk_s_int_key, s_nwk_s_int_key, nwk_s_enc_key, dev_nonce, join_req_type) FROM stdin;
1	2022-07-07 15:25:08.711725+00	\\x2232330000888802	\\x0000000000000000	\\x00c653b0	\\xf8e485b388f29719509af35a2c01fa25	\\xf8e485b388f29719509af35a2c01fa25	\\xf8e485b388f29719509af35a2c01fa25	22679	255
2	2022-07-11 10:22:35.891516+00	\\x2232330000888802	\\x0000000000000000	\\x00d9b080	\\x450fe099d870f07c5b487115533d11ca	\\x450fe099d870f07c5b487115533d11ca	\\x450fe099d870f07c5b487115533d11ca	43992	255
3	2022-07-12 08:03:33.068506+00	\\x2232330000888802	\\x0000000000000000	\\x0021051c	\\x77d76eef637ab48942bfd296a729e477	\\x77d76eef637ab48942bfd296a729e477	\\x77d76eef637ab48942bfd296a729e477	23794	255
\.


--
-- Data for Name: device_multicast_group; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.device_multicast_group (dev_eui, multicast_group_id, created_at) FROM stdin;
\.


--
-- Data for Name: device_profile; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.device_profile (created_at, updated_at, device_profile_id, supports_class_b, class_b_timeout, ping_slot_period, ping_slot_dr, ping_slot_freq, supports_class_c, class_c_timeout, mac_version, reg_params_revision, rx_delay_1, rx_dr_offset_1, rx_data_rate_2, rx_freq_2, factory_preset_freqs, max_eirp, max_duty_cycle, supports_join, rf_region, supports_32bit_fcnt, adr_algorithm_id) FROM stdin;
2022-07-07 15:24:19.162056+00	2022-07-07 15:24:19.162056+00	be018f1b-c068-43c0-a276-a7665ff090b4	f	0	0	0	0	t	0	1.0.2	RP002-1.0.3	0	0	0	0	\N	0	0	t	EU868	f	default
\.


--
-- Data for Name: device_queue; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.device_queue (id, created_at, updated_at, dev_eui, frm_payload, f_cnt, f_port, confirmed, is_pending, timeout_after, emit_at_time_since_gps_epoch, dev_addr, retry_after) FROM stdin;
\.


--
-- Data for Name: gateway; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.gateway (gateway_id, created_at, updated_at, first_seen_at, last_seen_at, location, altitude, gateway_profile_id, routing_profile_id, tls_cert, service_profile_id) FROM stdin;
\\xe45f01fffe7da7a8	2022-07-07 15:23:03.85329+00	2022-07-07 15:23:03.85329+00	2022-07-07 15:23:11.530283+00	2022-07-14 15:15:04.502669+00	(43.8855738,11.1051369)	0	\N	6d5db27e-4ce2-4b2b-b5d7-91f069397978	\\x	80ad5686-bc53-485a-8cd1-c342b5f087dc
\.


--
-- Data for Name: gateway_board; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.gateway_board (id, gateway_id, fpga_id, fine_timestamp_key) FROM stdin;
\.


--
-- Data for Name: gateway_profile; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.gateway_profile (gateway_profile_id, created_at, updated_at, channels, stats_interval) FROM stdin;
\.


--
-- Data for Name: gateway_profile_extra_channel; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.gateway_profile_extra_channel (id, gateway_profile_id, modulation, frequency, bandwidth, bitrate, spreading_factors) FROM stdin;
\.


--
-- Data for Name: multicast_group; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.multicast_group (id, created_at, updated_at, mc_addr, mc_nwk_s_key, f_cnt, group_type, dr, frequency, ping_slot_period, routing_profile_id, service_profile_id) FROM stdin;
\.


--
-- Data for Name: multicast_queue; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.multicast_queue (id, created_at, schedule_at, emit_at_time_since_gps_epoch, multicast_group_id, gateway_id, f_cnt, f_port, frm_payload, updated_at, retry_after) FROM stdin;
\.


--
-- Data for Name: routing_profile; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.routing_profile (created_at, updated_at, routing_profile_id, as_id, ca_cert, tls_cert, tls_key) FROM stdin;
2022-07-07 15:22:20.402499+00	2022-07-07 15:22:25.530279+00	6d5db27e-4ce2-4b2b-b5d7-91f069397978	chirpstack-application-server:8001
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.schema_migrations (version, dirty) FROM stdin;
33	f
\.


--
-- Data for Name: service_profile; Type: TABLE DATA; Schema: public; Owner: chirpstack_ns
--

COPY public.service_profile (created_at, updated_at, service_profile_id, ul_rate, ul_bucket_size, ul_rate_policy, dl_rate, dl_bucket_size, dl_rate_policy, add_gw_metadata, dev_status_req_freq, report_dev_status_battery, report_dev_status_margin, dr_min, dr_max, channel_mask, pr_allowed, hr_allowed, ra_allowed, nwk_geo_loc, target_per, min_gw_diversity, gws_private) FROM stdin;
2022-07-07 15:22:39.897215+00	2022-07-07 15:22:39.897215+00	80ad5686-bc53-485a-8cd1-c342b5f087dc	0	0	Drop	0	0	Drop	t	0	f	f	0	0	\\x	f	f	f	t	0	0	f
\.


--
-- Name: device_activation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chirpstack_ns
--

SELECT pg_catalog.setval('public.device_activation_id_seq', 3, true);


--
-- Name: device_queue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chirpstack_ns
--

SELECT pg_catalog.setval('public.device_queue_id_seq', 17, true);


--
-- Name: gateway_profile_extra_channel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chirpstack_ns
--

SELECT pg_catalog.setval('public.gateway_profile_extra_channel_id_seq', 1, false);


--
-- Name: multicast_queue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: chirpstack_ns
--

SELECT pg_catalog.setval('public.multicast_queue_id_seq', 1, false);


--
-- Name: code_migration code_migration_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.code_migration
    ADD CONSTRAINT code_migration_pkey PRIMARY KEY (id);


--
-- Name: device_activation device_activation_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device_activation
    ADD CONSTRAINT device_activation_pkey PRIMARY KEY (id);


--
-- Name: device_multicast_group device_multicast_group_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device_multicast_group
    ADD CONSTRAINT device_multicast_group_pkey PRIMARY KEY (multicast_group_id, dev_eui);


--
-- Name: device device_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_pkey PRIMARY KEY (dev_eui);


--
-- Name: device_profile device_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device_profile
    ADD CONSTRAINT device_profile_pkey PRIMARY KEY (device_profile_id);


--
-- Name: device_queue device_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device_queue
    ADD CONSTRAINT device_queue_pkey PRIMARY KEY (id);


--
-- Name: gateway_board gateway_board_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.gateway_board
    ADD CONSTRAINT gateway_board_pkey PRIMARY KEY (gateway_id, id);


--
-- Name: gateway gateway_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.gateway
    ADD CONSTRAINT gateway_pkey PRIMARY KEY (gateway_id);


--
-- Name: gateway_profile_extra_channel gateway_profile_extra_channel_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.gateway_profile_extra_channel
    ADD CONSTRAINT gateway_profile_extra_channel_pkey PRIMARY KEY (id);


--
-- Name: gateway_profile gateway_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.gateway_profile
    ADD CONSTRAINT gateway_profile_pkey PRIMARY KEY (gateway_profile_id);


--
-- Name: multicast_group multicast_group_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.multicast_group
    ADD CONSTRAINT multicast_group_pkey PRIMARY KEY (id);


--
-- Name: multicast_queue multicast_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.multicast_queue
    ADD CONSTRAINT multicast_queue_pkey PRIMARY KEY (id);


--
-- Name: routing_profile routing_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.routing_profile
    ADD CONSTRAINT routing_profile_pkey PRIMARY KEY (routing_profile_id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: service_profile service_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.service_profile
    ADD CONSTRAINT service_profile_pkey PRIMARY KEY (service_profile_id);


--
-- Name: idx_device_activation_dev_eui; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_device_activation_dev_eui ON public.device_activation USING btree (dev_eui);


--
-- Name: idx_device_activation_nonce_lookup; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_device_activation_nonce_lookup ON public.device_activation USING btree (join_eui, dev_eui, join_req_type, dev_nonce);


--
-- Name: idx_device_device_profile_id; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_device_device_profile_id ON public.device USING btree (device_profile_id);


--
-- Name: idx_device_mode; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_device_mode ON public.device USING btree (mode);


--
-- Name: idx_device_queue_confirmed; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_device_queue_confirmed ON public.device_queue USING btree (confirmed);


--
-- Name: idx_device_queue_dev_eui; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_device_queue_dev_eui ON public.device_queue USING btree (dev_eui);


--
-- Name: idx_device_queue_emit_at_time_since_gps_epoch; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_device_queue_emit_at_time_since_gps_epoch ON public.device_queue USING btree (emit_at_time_since_gps_epoch);


--
-- Name: idx_device_queue_timeout_after; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_device_queue_timeout_after ON public.device_queue USING btree (timeout_after);


--
-- Name: idx_device_routing_profile_id; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_device_routing_profile_id ON public.device USING btree (routing_profile_id);


--
-- Name: idx_device_service_profile_id; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_device_service_profile_id ON public.device USING btree (service_profile_id);


--
-- Name: idx_gateway_gateway_profile_id; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_gateway_gateway_profile_id ON public.gateway USING btree (gateway_profile_id);


--
-- Name: idx_gateway_profile_extra_channel_gw_profile_id; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_gateway_profile_extra_channel_gw_profile_id ON public.gateway_profile_extra_channel USING btree (gateway_profile_id);


--
-- Name: idx_gateway_routing_profile_id; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_gateway_routing_profile_id ON public.gateway USING btree (routing_profile_id);


--
-- Name: idx_gateway_service_profile_id; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_gateway_service_profile_id ON public.gateway USING btree (service_profile_id);


--
-- Name: idx_multicast_group_routing_profile_id; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_multicast_group_routing_profile_id ON public.multicast_group USING btree (routing_profile_id);


--
-- Name: idx_multicast_group_service_profile_id; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_multicast_group_service_profile_id ON public.multicast_group USING btree (service_profile_id);


--
-- Name: idx_multicast_queue_emit_at_time_since_gps_epoch; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_multicast_queue_emit_at_time_since_gps_epoch ON public.multicast_queue USING btree (emit_at_time_since_gps_epoch);


--
-- Name: idx_multicast_queue_multicast_group_id; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_multicast_queue_multicast_group_id ON public.multicast_queue USING btree (multicast_group_id);


--
-- Name: idx_multicast_queue_schedule_at; Type: INDEX; Schema: public; Owner: chirpstack_ns
--

CREATE INDEX idx_multicast_queue_schedule_at ON public.multicast_queue USING btree (schedule_at);


--
-- Name: device_activation device_activation_dev_eui_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device_activation
    ADD CONSTRAINT device_activation_dev_eui_fkey FOREIGN KEY (dev_eui) REFERENCES public.device(dev_eui) ON DELETE CASCADE;


--
-- Name: device device_device_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_device_profile_id_fkey FOREIGN KEY (device_profile_id) REFERENCES public.device_profile(device_profile_id) ON DELETE CASCADE;


--
-- Name: device_multicast_group device_multicast_group_dev_eui_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device_multicast_group
    ADD CONSTRAINT device_multicast_group_dev_eui_fkey FOREIGN KEY (dev_eui) REFERENCES public.device(dev_eui) ON DELETE CASCADE;


--
-- Name: device_multicast_group device_multicast_group_multicast_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device_multicast_group
    ADD CONSTRAINT device_multicast_group_multicast_group_id_fkey FOREIGN KEY (multicast_group_id) REFERENCES public.multicast_group(id) ON DELETE CASCADE;


--
-- Name: device_queue device_queue_dev_eui_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device_queue
    ADD CONSTRAINT device_queue_dev_eui_fkey FOREIGN KEY (dev_eui) REFERENCES public.device(dev_eui) ON DELETE CASCADE;


--
-- Name: device device_routing_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_routing_profile_id_fkey FOREIGN KEY (routing_profile_id) REFERENCES public.routing_profile(routing_profile_id) ON DELETE CASCADE;


--
-- Name: device device_service_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.device
    ADD CONSTRAINT device_service_profile_id_fkey FOREIGN KEY (service_profile_id) REFERENCES public.service_profile(service_profile_id) ON DELETE CASCADE;


--
-- Name: gateway_board gateway_board_gateway_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.gateway_board
    ADD CONSTRAINT gateway_board_gateway_id_fkey FOREIGN KEY (gateway_id) REFERENCES public.gateway(gateway_id) ON DELETE CASCADE;


--
-- Name: gateway gateway_gateway_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.gateway
    ADD CONSTRAINT gateway_gateway_profile_id_fkey FOREIGN KEY (gateway_profile_id) REFERENCES public.gateway_profile(gateway_profile_id);


--
-- Name: gateway_profile_extra_channel gateway_profile_extra_channel_gateway_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.gateway_profile_extra_channel
    ADD CONSTRAINT gateway_profile_extra_channel_gateway_profile_id_fkey FOREIGN KEY (gateway_profile_id) REFERENCES public.gateway_profile(gateway_profile_id) ON DELETE CASCADE;


--
-- Name: gateway gateway_routing_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.gateway
    ADD CONSTRAINT gateway_routing_profile_id_fkey FOREIGN KEY (routing_profile_id) REFERENCES public.routing_profile(routing_profile_id) ON DELETE CASCADE;


--
-- Name: gateway gateway_service_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.gateway
    ADD CONSTRAINT gateway_service_profile_id_fkey FOREIGN KEY (service_profile_id) REFERENCES public.service_profile(service_profile_id) ON DELETE CASCADE;


--
-- Name: multicast_group multicast_group_routing_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.multicast_group
    ADD CONSTRAINT multicast_group_routing_profile_id_fkey FOREIGN KEY (routing_profile_id) REFERENCES public.routing_profile(routing_profile_id) ON DELETE CASCADE;


--
-- Name: multicast_group multicast_group_service_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.multicast_group
    ADD CONSTRAINT multicast_group_service_profile_id_fkey FOREIGN KEY (service_profile_id) REFERENCES public.service_profile(service_profile_id) ON DELETE CASCADE;


--
-- Name: multicast_queue multicast_queue_gateway_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.multicast_queue
    ADD CONSTRAINT multicast_queue_gateway_id_fkey FOREIGN KEY (gateway_id) REFERENCES public.gateway(gateway_id) ON DELETE CASCADE;


--
-- Name: multicast_queue multicast_queue_multicast_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: chirpstack_ns
--

ALTER TABLE ONLY public.multicast_queue
    ADD CONSTRAINT multicast_queue_multicast_group_id_fkey FOREIGN KEY (multicast_group_id) REFERENCES public.multicast_group(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--
