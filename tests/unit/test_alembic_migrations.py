from alchemy import alembic_migrations


def test_apply_alembic_migrations_upgrades_to_head(mocker):
    upgrade = mocker.patch.object(alembic_migrations.command, "upgrade")

    alembic_migrations.apply_alembic_migrations()

    config, revision = upgrade.call_args.args
    assert revision == "head"
    assert config.get_main_option("script_location") == str(alembic_migrations.dir_path)
