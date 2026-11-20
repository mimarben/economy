-- Economy App Database Schema
-- Generated from migrations (head: c202411200001)
-- This file represents the CURRENT state of the database

BEGIN;


-- ======================
-- CORE TABLES
-- ======================

CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

CREATE TABLE IF NOT EXISTS banks (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS sources (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    active BOOLEAN NOT NULL,
    type VARCHAR(10) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS places (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    active BOOLEAN NOT NULL,
    type VARCHAR(10) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS expenses_categories (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS incomes_categories (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS investments_categories (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS households (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    address VARCHAR NOT NULL,
    description VARCHAR,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id)
);

-- ======================
-- ACCOUNTS & USERS
-- ======================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    surname1 VARCHAR NOT NULL,
    surname2 VARCHAR,
    dni VARCHAR NOT NULL,
    email VARCHAR,
    active BOOLEAN NOT NULL,
    telephone INTEGER,
    role VARCHAR(6) NOT NULL,
    password VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_users_dni UNIQUE (dni)
);

CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    iban VARCHAR NOT NULL,
    balance NUMERIC(20, 10),
    active BOOLEAN NOT NULL,
    bank_id INTEGER NOT NULL,
    import_origin_id INTEGER,
    import_profile_id INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_accounts_iban UNIQUE (iban),
    CONSTRAINT accounts_bank_id_fkey FOREIGN KEY (bank_id) REFERENCES banks (id),
    CONSTRAINT accounts_import_origin_id_fkey FOREIGN KEY (import_origin_id) REFERENCES import_origins (id),
    CONSTRAINT accounts_import_profile_id_fkey FOREIGN KEY (import_profile_id) REFERENCES import_profiles (id)
);

CREATE TABLE IF NOT EXISTS account_users (
    id SERIAL NOT NULL,
    account_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_account_user UNIQUE (account_id, user_id),
    CONSTRAINT account_users_account_id_fkey FOREIGN KEY (account_id) REFERENCES accounts (id),
    CONSTRAINT account_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id)
);

-- ======================
-- FINANCIAL TRANSACTIONS
-- ======================

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    amount NUMERIC NOT NULL,
    date DATE NOT NULL,
    currency VARCHAR(9) NOT NULL,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    account_id INTEGER,
    ignore_in_analysis BOOLEAN DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_expenses_user_id FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_expenses_category_id FOREIGN KEY (category_id) REFERENCES expenses_categories (id),
    CONSTRAINT fk_expenses_source_id FOREIGN KEY (source_id) REFERENCES sources (id),
    CONSTRAINT fk_expenses_account_id FOREIGN KEY (account_id) REFERENCES accounts (id)
);

CREATE TABLE IF NOT EXISTS incomes (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    amount NUMERIC NOT NULL,
    date DATE NOT NULL,
    currency VARCHAR(9) NOT NULL,
    user_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    account_id INTEGER,
    ignore_in_analysis BOOLEAN DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_incomes_user_id FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_incomes_category_id FOREIGN KEY (category_id) REFERENCES incomes_categories (id),
    CONSTRAINT fk_incomes_source_id FOREIGN KEY (source_id) REFERENCES sources (id),
    CONSTRAINT fk_incomes_account_id FOREIGN KEY (account_id) REFERENCES accounts (id)
);

CREATE TABLE IF NOT EXISTS savings (
    id SERIAL NOT NULL,
    description VARCHAR,
    amount NUMERIC(12, 2) NOT NULL,
    date DATE NOT NULL,
    currency VARCHAR(9) NOT NULL,
    user_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_savings_user_id FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_savings_account_id FOREIGN KEY (account_id) REFERENCES accounts (id)
);

CREATE TABLE IF NOT EXISTS savings_logs (
    id SERIAL NOT NULL,
    date DATE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    total_amount NUMERIC(12, 2),
    note VARCHAR,
    saving_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_savings_logs_saving_id FOREIGN KEY (saving_id) REFERENCES savings (id),
    CONSTRAINT fk_savings_logs_source_id FOREIGN KEY (source_id) REFERENCES sources (id)
);

-- ======================
-- INVESTMENTS (with ISIN support)
-- ======================

CREATE TABLE IF NOT EXISTS investments (
    id SERIAL NOT NULL,
    description VARCHAR NOT NULL,
    date DATE NOT NULL,
    currency VARCHAR(9) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    dedup_hash VARCHAR(64) NOT NULL,
    isin VARCHAR(12),
    account_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_investments_account_dedup_hash UNIQUE (account_id, dedup_hash),
    CONSTRAINT fk_investments_account_id FOREIGN KEY (account_id) REFERENCES accounts (id),
    CONSTRAINT fk_investments_category_id FOREIGN KEY (category_id) REFERENCES investments_categories (id)
);

CREATE INDEX ix_investments_isin ON investments (isin);

ALTER TABLE investments ADD COLUMN instrument_id INTEGER;
ALTER TABLE investments ADD COLUMN source_id INTEGER;
ALTER TABLE investments ADD CONSTRAINT fk_investments_instrument FOREIGN KEY (instrument_id) REFERENCES instruments (id);
ALTER TABLE investments ADD CONSTRAINT fk_investments_source FOREIGN KEY (source_id) REFERENCES sources (id);

ALTER TABLE investments_logs ADD COLUMN fees NUMERIC(18, 10);
ALTER TABLE investments_logs ADD COLUMN external_ref VARCHAR(255);

ALTER TABLE market_quotes ADD COLUMN instrument_id INTEGER;
ALTER TABLE market_quotes ADD COLUMN quoted_at TIMESTAMP;
ALTER TABLE market_quotes ADD COLUMN price_type VARCHAR(16);
ALTER TABLE market_quotes ADD CONSTRAINT fk_market_quotes_instrument FOREIGN KEY (instrument_id) REFERENCES instruments (id);

CREATE TABLE IF NOT EXISTS instruments (
    id SERIAL NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    asset_class VARCHAR(32) NOT NULL,
    category_id INTEGER NOT NULL,
    instrument_type VARCHAR(32),
    currency VARCHAR(8) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_instruments_category_id FOREIGN KEY (category_id) REFERENCES investments_categories (id)
);

CREATE INDEX ix_instruments_name ON instruments (name);
CREATE INDEX ix_instruments_instrument_type ON instruments (instrument_type);

CREATE TABLE IF NOT EXISTS instrument_identifiers (
    id SERIAL NOT NULL,
    instrument_id INTEGER NOT NULL,
    identifier_type VARCHAR(16) NOT NULL,
    value VARCHAR(64) NOT NULL,
    exchange VARCHAR(16),
    provider VARCHAR(32),
    is_primary BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_instrument_identifiers_instrument_id FOREIGN KEY (instrument_id) REFERENCES instruments (id) ON DELETE CASCADE,
    CONSTRAINT uq_instrument_identifier_namespace UNIQUE (identifier_type, value, COALESCE(NULLIF(exchange, ''), ''), COALESCE(NULLIF(provider, ''), ''))
);

CREATE TABLE IF NOT EXISTS instrument_compositions (
    id SERIAL NOT NULL,
    parent_instrument_id INTEGER NOT NULL,
    child_instrument_id INTEGER NOT NULL,
    quantity NUMERIC(18, 10) NOT NULL,
    weight NUMERIC(18, 10),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_instrument_compositions_parent FOREIGN KEY (parent_instrument_id) REFERENCES instruments (id) ON DELETE CASCADE,
    CONSTRAINT fk_instrument_compositions_child FOREIGN KEY (child_instrument_id) REFERENCES instruments (id) ON DELETE CASCADE,
    CONSTRAINT uq_instrument_composition_unique UNIQUE (parent_instrument_id, child_instrument_id)
);

CREATE INDEX ix_instrument_compositions_parent ON instrument_compositions (parent_instrument_id);
CREATE INDEX ix_instrument_compositions_child ON instrument_compositions (child_instrument_id);

CREATE TABLE IF NOT EXISTS fx_rates (
    id SERIAL NOT NULL,
    base_currency VARCHAR(8) NOT NULL,
    target_currency VARCHAR(8) NOT NULL,
    rate NUMERIC(18, 10) NOT NULL,
    source VARCHAR(32) NOT NULL,
    published_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT uq_fx_rate_unique UNIQUE (base_currency, target_currency, source, published_at)
);

CREATE INDEX ix_fx_rate_base_target ON fx_rates (base_currency, target_currency);

CREATE TABLE IF NOT EXISTS market_quote_history (
    id SERIAL NOT NULL,
    instrument_id INTEGER NOT NULL,
    price NUMERIC(18, 10) NOT NULL,
    quoted_at TIMESTAMP NOT NULL,
    price_type VARCHAR(16),
    source VARCHAR(32),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_market_quote_history_instrument_id FOREIGN KEY (instrument_id) REFERENCES instruments (id) ON DELETE CASCADE
);

CREATE INDEX ix_market_quote_history_instrument ON market_quote_history (instrument_id);
CREATE INDEX ix_market_quote_history_quoted_at ON market_quote_history (quoted_at);

CREATE TABLE IF NOT EXISTS investments_logs (
    id SERIAL NOT NULL,
    date DATE NOT NULL,
    current_value NUMERIC(12, 2),
    price_per_unit NUMERIC(12, 6),
    quantity NUMERIC(12, 6),
    action VARCHAR(8) NOT NULL,
    note VARCHAR,
    investment_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_investments_logs_investment_id FOREIGN KEY (investment_id) REFERENCES investments (id)
);

-- ======================
-- MARKET QUOTES (cache)
-- ======================

CREATE TABLE IF NOT EXISTS market_quotes (
    id SERIAL NOT NULL,
    isin VARCHAR(12) NOT NULL,
    symbol VARCHAR(32),
    name VARCHAR(255),
    instrument_type VARCHAR(32),
    currency VARCHAR(8),
    last_price NUMERIC(18, 6),
    previous_close NUMERIC(18, 6),
    source VARCHAR(20),
    fetched_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_market_quotes_isin UNIQUE (isin)
);

CREATE INDEX ix_market_quotes_isin ON market_quotes (isin);

-- ======================
-- HOUSEHOLD MEMBERSHIP
-- ======================

CREATE TABLE IF NOT EXISTS households_members (
    id SERIAL NOT NULL,
    role VARCHAR(7) NOT NULL,
    active BOOLEAN NOT NULL,
    household_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_households_members_household_id FOREIGN KEY (household_id) REFERENCES households (id),
    CONSTRAINT fk_households_members_user_id FOREIGN KEY (user_id) REFERENCES users (id)
);

-- ======================
-- CATEGORY RULES (auto-categorization)
-- ======================

CREATE TABLE IF NOT EXISTS category_rules (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    condition_json JSONB NOT NULL,
    category_id INTEGER NOT NULL,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_category_rules_category_id FOREIGN KEY (category_id) REFERENCES expenses_categories (id)
);

CREATE TABLE IF NOT EXISTS source_rules (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    source_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_source_rules_source_id FOREIGN KEY (source_id) REFERENCES sources (id),
    CONSTRAINT fk_source_rules_category_id FOREIGN KEY (category_id) REFERENCES expenses_categories (id)
);

-- ======================
-- CARDS
-- ======================

CREATE TABLE IF NOT EXISTS cards (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    last_four VARCHAR(4),
    brand VARCHAR(32),
    type VARCHAR(16),
    balance NUMERIC(20, 10),
    credit_limit NUMERIC(20, 10),
    active BOOLEAN NOT NULL,
    account_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_cards_account_id FOREIGN KEY (account_id) REFERENCES accounts (id)
);

-- ======================
-- IMPORT MANAGEMENT
-- ======================

CREATE TABLE IF NOT EXISTS import_origins (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    type VARCHAR(32),
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS import_profiles (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    config_json JSONB,
    active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id)
);

-- ======================
-- FINANCIAL SUMMARIES
-- ======================

CREATE TABLE IF NOT EXISTS financials_summaries (
    id SERIAL NOT NULL,
    date DATE NOT NULL,
    total_income NUMERIC NOT NULL,
    total_expenses NUMERIC NOT NULL,
    total_savings NUMERIC NOT NULL,
    total_investments NUMERIC NOT NULL,
    net_worth NUMERIC NOT NULL,
    user_id INTEGER NOT NULL,
    household_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    deleted_at TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_summaries_user_id FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_summaries_household_id FOREIGN KEY (household_id) REFERENCES households (id)
);


COMMIT;
