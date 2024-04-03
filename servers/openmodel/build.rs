use std::path::PathBuf;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let original_out_dir = PathBuf::from(std::env::var("OUT_DIR")?);
    let out_dir = "./src/proto";

    let proto_dir = match std::env::var("PROTO_DIR") {
        Ok(dir) => PathBuf::from(dir),
        Err(_) => PathBuf::from("../../protos"),
    };

    let mut openmodel_v1_config = prost_build::Config::new();
    openmodel_v1_config.default_package_filename("openmodel.v1");
    tonic_build::configure()
        .out_dir(out_dir)
        .file_descriptor_set_path(original_out_dir.join("openmodel_v1_descriptor.bin"))
        .compile_with_config(
            openmodel_v1_config,
            &[proto_dir.join("openmodel/v1/model.proto").to_str().unwrap()],
            &[proto_dir.to_str().unwrap()],
        )?;

    let mut openmodel_v2_config = prost_build::Config::new();
    openmodel_v2_config.default_package_filename("openmodel.v2");
    tonic_build::configure()
        .out_dir(out_dir)
        .file_descriptor_set_path(original_out_dir.join("openmodel_v2_descriptor.bin"))
        .compile_with_config(
            openmodel_v2_config,
            &[proto_dir
                .join("openmodel/v2/inference.proto")
                .to_str()
                .unwrap()],
            &[proto_dir.to_str().unwrap()],
        )?;

    Ok(())
}
