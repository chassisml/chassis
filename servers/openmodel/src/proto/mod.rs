pub mod openmodel {
    pub mod v1 {
        include!("openmodel.v1.rs");

        pub const FILE_DESCRIPTOR_SET: &[u8] =
            tonic::include_file_descriptor_set!("openmodel_v1_descriptor");
    }

    pub mod v2 {
        include!("openmodel.v2.rs");

        pub const FILE_DESCRIPTOR_SET: &[u8] =
            tonic::include_file_descriptor_set!("openmodel_v2_descriptor");
    }
}
